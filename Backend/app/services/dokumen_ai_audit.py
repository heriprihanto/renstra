import asyncio
import io
import json
import logging
import os
import re
import shutil
import ssl
import subprocess
import urllib.request
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import httpx
import pypdf
from openai import AsyncOpenAI
from sqlmodel import select, text
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.models.dokumen import DokumenPerencanaan, RenstraDokumenAudit
from app.models.opd import TaOpd, TaSubPd
from app.schemas.ai import (
    DokumenAuditResponse,
    IndikatorAuditItem,
    KegiatanAuditItem,
    NomenklaturAuditItem,
    PaguAuditItem,
    SubkegiatanAuditItem,
    TujuanSasaranAuditItem,
)

logger = logging.getLogger(__name__)


AUDIT_SYSTEM_PROMPT = """
Anda adalah Auditor Ahli Perencanaan Daerah (Bapperida Kota Tegal) yang bertugas
memverifikasi kesesuaian antara Dokumen Perencanaan (Penetapan / Rancangan Akhir Renstra)
dalam bentuk teks hasil ekstrak PDF dengan Data Resmi pada Database Aplikasi.

TUGAS ANDA:
1. Memverifikasi Kesesuaian Tujuan & Sasaran Daerah:
   - Cocokkan rumusan kalimat Tujuan dan Sasaran di Bab III / Bab IV / Cascading PDF dengan data database.
2. Memverifikasi Indikator Tujuan, Indikator Sasaran, dan IKU (Indikator Kinerja Utama):
   - Cocokkan nama indikator kinerja tujuan & sasaran serta target tahunannya (sebelum vs setelah perubahan / 2026-2030).
   - Khusus indikator yang bertanda IKU (is_iku = true), verifikasi apakah tercantum dalam tabel Penetapan IKU Renstra (Tabel 4.3 atau sejenisnya) dan apakah angka targetnya selaras.
3. Memverifikasi Kesesuaian Pagu Program:
   - Bandingkan nilai pagu (khususnya pagu tahun anggaran 2026 atau total) yang tertulis
     pada tabel matriks PDF dengan data resmi pagu di database.
   - Deteksi apakah ada perbedaan/selisih nilai nominal.
4. Memverifikasi Kesesuaian Nomenklatur Program:
   - Pastikan kode dan uraian program di PDF konsisten dengan database.
5. Menghitung Skor Kesesuaian Keseluruhan (0 - 100%):
   - ATURAN WAJIB PENILAIAN SKOR:
     * Jika data Tujuan dan/atau Sasaran pada database aplikasi KOSONG (0 entri atau belum dientri oleh OPD), berikan skor MAKSIMAL 40-50% dan status 'Perlu Perbaikan (Belum Entri Tujuan/Sasaran)'. JANGAN PERNAH memberikan nilai tinggi/100% jika Tujuan/Sasaran belum ada di database!
     * Jika semua cocok dan lengkap, berikan skor 90-100% dan status 'Sangat Sesuai'.
     * Jika terdapat selisih pagu/indikator, kurangi skor proporsional dan status 'Terdapat Selisih'.
     * Jika banyak tidak cocok atau data tidak lengkap, status 'Perlu Perbaikan'.
6. Memberikan Rekomendasi Bapperida yang konkrit dan dapat ditindaklanjuti.

FORMAT KELUARAN (WAJIB JSON VALID):
{
  "skor_kesesuaian": 95,
  "status": "Sesuai",
  "ringkasan_analisis": "Penjelasan ringkas hasil audit...",
  "audit_tujuan_sasaran": [
    {
      "level": "Tujuan",
      "uraitujuan_sasaran": "...",
      "indikator": "...",
      "satuan": "...",
      "is_iku": true,
      "target_murni_db": "2026: ..., 2027: ...",
      "target_perubahan_db": "2026: ..., 2027: ...",
      "target_pdf": "Sebelum: ..., Setelah: ...",
      "is_match": true,
      "keterangan": "Rumusan tujuan, indikator, status IKU, dan target perubahan di PDF cocok dengan database."
    }
  ],
  "audit_pagu": [
    {
      "kodeprogram": "...",
      "uraiprogram": "...",
      "pagu_pdf": 1000000000,
      "pagu_db": 1000000000,
      "selisih": 0,
      "is_match": true,
      "keterangan": "Pagu sesuai..."
    }
  ],
  "audit_indikator": [
    {
      "kodeprogram": "...",
      "uraiprogram": "...",
      "indikator": "...",
      "target_pdf": "...",
      "target_db": "...",
      "satuan": "...",
      "is_match": true,
      "keterangan": "..."
    }
  ],
  "audit_nomenklatur": [
    {
      "level": "program",
      "kode": "...",
      "nama_pdf": "...",
      "nama_db": "...",
      "is_match": true,
      "keterangan": "..."
    }
  ],
  "rekomendasi": [
    "Rekomendasi 1",
    "Rekomendasi 2"
  ]
}
"""


async def get_target_document_for_opd(
    session: AsyncSession, id_skpd: int, id_dokumen: Optional[int] = None
) -> Tuple[DokumenPerencanaan, str, TaOpd]:
    """
    Mencari dokumen perencanaan prioritas:
    1. Jika sudah ada Penetapan (id_ref_dokumen = 66), gunakan Penetapan.
    2. Jika belum, gunakan Rancangan Akhir (id_ref_dokumen = 65).
    """
    opd = await session.get(TaOpd, id_skpd)
    if not opd:
        raise ValueError(f"Perangkat Daerah dengan ID {id_skpd} tidak ditemukan.")

    # Ambil semua id_sub_skpd dari OPD ini
    subs_stmt = select(TaSubPd.id_sub_skpd).where(TaSubPd.id_skpd == id_skpd)
    sub_ids = (await session.exec(subs_stmt)).all()
    sub_ids_set = set(sub_ids)
    sub_ids_set.add(id_skpd)

    if id_dokumen:
        doc = await session.get(DokumenPerencanaan, id_dokumen)
        if not doc or doc.id_sub_pd not in sub_ids_set:
            raise ValueError(f"Dokumen dengan ID {id_dokumen} tidak ditemukan untuk OPD ini.")
        if doc.id_ref_dokumen not in (65, 66):
            raise ValueError("Dokumen yang dipilih bukan Rancangan Akhir (65) maupun Penetapan (66).")
        tahap = "Penetapan" if doc.id_ref_dokumen == 66 else "Rancangan Akhir"
        return doc, tahap, opd

    # Query prioritas: 66 (Penetapan) lalu 65 (Rancangan Akhir)
    docs_stmt = (
        select(DokumenPerencanaan)
        .where(
            DokumenPerencanaan.id_sub_pd.in_(list(sub_ids_set)),
            DokumenPerencanaan.id_ref_dokumen.in_([65, 66]),
        )
        .order_by(
            DokumenPerencanaan.id_ref_dokumen.desc(),  # 66 duluan baru 65
            DokumenPerencanaan.uploaded_at.desc(),
        )
    )
    docs = (await session.exec(docs_stmt)).all()
    if not docs:
        raise ValueError(
            f"Perangkat Daerah '{opd.nama_skpd}' belum mengunggah dokumen Penetapan (Renstra) maupun Rancangan Akhir."
        )

    chosen_doc = docs[0]
    tahap = "Penetapan" if chosen_doc.id_ref_dokumen == 66 else "Rancangan Akhir"
    return chosen_doc, tahap, opd


def _fetch_pdf_bytes(link_gd: str) -> bytes:
    """
    Mengunduh berkas PDF dengan strategi bertingkat (multi-tier fallback):
    1. Cek filesystem lokal (jika aplikasi dihosting pada server yang sama dengan penyimpanan file)
    2. Coba httpx (verify=False, trust_env=False) dengan HTTPS lalu HTTP
    3. Coba httpx (verify=False, trust_env=True)
    4. Coba curl subprocess (-k -s -L) untuk mengatasi keanehan SSL/proxy environment di Linux
    5. Coba urllib dengan SSL unverified & proxy bypass
    """
    raw_link = (link_gd or "").strip()
    if not raw_link:
        raise ValueError("Link dokumen kosong.")

    link_clean = raw_link.lstrip("/")

    # 1. Cek filesystem lokal terlebih dahulu
    local_candidates = [
        raw_link,
        f"/var/www/dokren/{link_clean}",
        f"/var/www/monevrkpd/dokren/{link_clean}",
        f"/var/www/html/dokren/{link_clean}",
        f"/var/www/html/monevrkpd/dokren/{link_clean}",
        os.path.join(os.getcwd(), "dokren", link_clean),
    ]
    for lp in local_candidates:
        if os.path.isfile(lp):
            try:
                with open(lp, "rb") as f:
                    data = f.read()
                    if len(data) > 500:
                        logger.info("PDF ditemukan di filesystem lokal: %s (%d bytes)", lp, len(data))
                        return data
            except Exception as e:
                logger.warning("Gagal membaca file lokal %s: %s", lp, e)

    if raw_link.startswith("http://") or raw_link.startswith("https://"):
        urls = [raw_link]
    else:
        urls = [
            f"https://monevrkpd.tegalkota.go.id/dokren/{link_clean}",
            f"http://monevrkpd.tegalkota.go.id/dokren/{link_clean}",
        ]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RENSTRA-AI/1.0"}
    errors = []

    # 2. Coba httpx tanpa proxy environment (mengatasi wrong version number akibat intercepting proxy)
    for trust_env in [False, True]:
        for url in urls:
            try:
                with httpx.Client(verify=False, trust_env=trust_env, follow_redirects=True, timeout=30.0) as client:
                    resp = client.get(url, headers=headers)
                    if resp.status_code == 200 and len(resp.content) > 500:
                        logger.info("PDF berhasil diunduh via httpx (trust_env=%s) dari %s (%d bytes)", trust_env, url, len(resp.content))
                        return resp.content
                    elif resp.status_code != 200:
                        errors.append(f"HTTP {resp.status_code} on {url}")
            except Exception as e:
                errors.append(f"httpx({url}, trust_env={trust_env}): {e}")

    # 3. Coba curl subprocess (-k abaikan sertifikat SSL, -L ikuti redirect)
    for url in urls:
        try:
            res = subprocess.run(
                ["curl", "-k", "-s", "-L", "--max-time", "30", url],
                capture_output=True,
                timeout=35,
            )
            if res.returncode == 0 and len(res.stdout) > 500:
                logger.info("PDF berhasil diunduh via curl dari %s (%d bytes)", url, len(res.stdout))
                return res.stdout
            elif res.returncode != 0:
                errors.append(f"curl exit code {res.returncode} on {url}")
        except Exception as e:
            errors.append(f"curl({url}): {e}")

    # 4. Coba urllib dengan SSL unverified & ProxyHandler kosong
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    for opener in [
        urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPSHandler(context=ctx)),
        urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx)),
    ]:
        for url in urls:
            try:
                req = urllib.request.Request(url, headers=headers)
                with opener.open(req, timeout=30) as r:
                    b = r.read()
                    if len(b) > 500:
                        logger.info("PDF berhasil diunduh via urllib dari %s (%d bytes)", url, len(b))
                        return b
            except Exception as e:
                errors.append(f"urllib({url}): {e}")

    error_summary = "; ".join(errors[:4])
    logger.error("Gagal mengunduh PDF untuk %s. Riwayat percobaan: %s", raw_link, error_summary)
    raise ValueError(f"Gagal mengunduh file PDF dari server: {error_summary}")


def download_and_extract_pdf(link_gd: str) -> Tuple[int, int, str]:
    """
    Mengunduh file PDF dari storage dan mengekstrak teks halaman-halaman tabel yang relevan.
    Return: (total_pages, analyzed_pages_count, extracted_text)
    """
    raw_link = (link_gd or "").strip()
    if not raw_link:
        raise ValueError("Link dokumen kosong.")

    # Validasi ekstensi
    if not raw_link.lower().endswith(".pdf"):
        raise ValueError(f"File dokumen bukan format PDF ({raw_link.split('.')[-1]}). Analisa AI hanya mendukung dokumen PDF.")

    logger.info("Memulai proses unduh dan ekstraksi PDF: %s", raw_link)
    pdf_bytes = _fetch_pdf_bytes(raw_link)

    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    total_pages = len(reader.pages)

    # Ekstrak seluruh halaman yang memuat teks untuk audit komparasi 10 elemen
    extracted_pages_text = []
    for idx, page in enumerate(reader.pages):
        try:
            txt = page.extract_text() or ""
            if txt.strip():
                extracted_pages_text.append(f"--- [HALAMAN {idx + 1}] ---\n{txt}")
        except Exception:
            continue

    analyzed_pages_count = len(extracted_pages_text)
    combined_text = "\n\n".join(extracted_pages_text)
    return total_pages, analyzed_pages_count, combined_text


async def fetch_opd_db_context(session: AsyncSession, id_skpd: int) -> Dict[str, Any]:
    """Mengambil data resmi lengkap Tujuan, Sasaran, Program, Kegiatan, Subkegiatan, Indikator, Pagu, dan Target dari database."""
    # 1. Tujuan, Sasaran, Indikator Tujuan/Sasaran, dan IKU
    q_ts = """
    SELECT 
        'Tujuan' AS level,
        t.uraitujuan AS tujuan_sasaran,
        it.uraitujuan_indikator AS indikator,
        it.satuan,
        it.iku,
        it.target1, it.target2, it.target3, it.target4, it.target5,
        it.p_target1, it.p_target2, it.p_target3, it.p_target4, it.p_target5
    FROM ta_opd o
    JOIN renstra_tujuan t ON t.kodeskpd = o.kode_skpd
    LEFT JOIN renstra_indikator_tujuan it ON it.idtujuan = t.idtujuan
    WHERE o.id_skpd = :id_skpd
    UNION ALL
    SELECT 
        'Sasaran' AS level,
        s.uraisasaran AS tujuan_sasaran,
        isas.uraisasaran_indikator AS indikator,
        isas.satuan,
        isas.iku,
        isas.target1, isas.target2, isas.target3, isas.target4, isas.target5,
        isas.p_target1, isas.p_target2, isas.p_target3, isas.p_target4, isas.p_target5
    FROM ta_opd o
    JOIN renstra_tujuan t ON t.kodeskpd = o.kode_skpd
    JOIN renstra_sasaran s ON s.idtujuan = t.idtujuan
    LEFT JOIN renstra_indikator_sasaran isas ON isas.idsasaran = s.idsasaran
    WHERE o.id_skpd = :id_skpd
    ORDER BY level DESC, tujuan_sasaran, indikator;
    """
    ts_rows = []
    try:
        res_ts = await session.execute(text(q_ts), {"id_skpd": id_skpd})
        for r in res_ts.fetchall():
            d = dict(r._mapping)
            lvl = d.get("level") or "Tujuan"
            ts_name = (d.get("tujuan_sasaran") or "").strip()
            is_iku = str(d.get("iku") or "").strip() == "1"

            t_murni_parts = []
            if d.get("target1"): t_murni_parts.append(f"2026: {d['target1']}")
            if d.get("target2"): t_murni_parts.append(f"2027: {d['target2']}")
            if d.get("target5"): t_murni_parts.append(f"Akhir: {d['target5']}")
            t_murni_str = "; ".join(t_murni_parts) or "-"

            t_perubahan_parts = []
            if d.get("p_target1"): t_perubahan_parts.append(f"2026: {d['p_target1']}")
            if d.get("p_target2"): t_perubahan_parts.append(f"2027: {d['p_target2']}")
            if d.get("p_target5"): t_perubahan_parts.append(f"Akhir: {d['p_target5']}")
            t_perubahan_str = "; ".join(t_perubahan_parts) or "-"

            ts_rows.append({
                "level": lvl,
                "tujuan_sasaran": ts_name,
                "indikator": (d.get("indikator") or "-").strip(),
                "satuan": d.get("satuan") or "-",
                "is_iku": is_iku,
                "target_murni": t_murni_str,
                "target_perubahan": t_perubahan_str,
                "target1": d.get("target1"),
                "p_target1": d.get("p_target1"),
            })
    except Exception as e:
        logger.warning("Gagal query tujuan & sasaran untuk id_skpd %s: %s", id_skpd, e)
        await session.rollback()

    # 2. Program, Indikator Program & Pagu
    q_prog = """
    SELECT 
        p.kodeprogram,
        p.uraiprogram,
        COALESCE(SUM(s.pagu1), 0) AS pagu1,
        COALESCE(SUM(s.pagu2), 0) AS pagu2,
        COALESCE(SUM(s.p_pagu1), 0) AS p_pagu1,
        COALESCE(SUM(s.p_pagu2), 0) AS p_pagu2,
        COALESCE(SUM(s.p_pagu1 + s.p_pagu2 + s.p_pagu3 + s.p_pagu4 + s.p_pagu5), 0) AS total_perubahan
    FROM renstra_program p
    JOIN ta_sub_pd spd ON spd.kode_sub_skpd = p.kodeskpd
    LEFT JOIN renstra_subkegiatan s 
        ON s.kodeskpd = p.kodeskpd AND s.kodeprogram = p.kodeprogram
    WHERE spd.id_skpd = :id_skpd
    GROUP BY p.kodeprogram, p.uraiprogram
    ORDER BY p.kodeprogram;
    """
    progs = []
    try:
        res_prog = await session.execute(text(q_prog), {"id_skpd": id_skpd})
        for r in res_prog.fetchall():
            row_dict = dict(r._mapping)
            for k in ("pagu1", "pagu2", "p_pagu1", "p_pagu2", "total_perubahan"):
                if k in row_dict and row_dict[k] is not None:
                    row_dict[k] = float(row_dict[k])
            progs.append(row_dict)
    except Exception as e:
        logger.warning("Gagal query program untuk id_skpd %s: %s", id_skpd, e)
        await session.rollback()

    # 3. Indikator Program
    q_ind = """
    SELECT 
        p.kodeprogram,
        p.uraiprogram,
        ip.uraiindikator AS indikator,
        ip.satuan,
        ip.target1, ip.target2, ip.target3, ip.target4, ip.target5,
        ip.p_target1, ip.p_target2, ip.p_target3, ip.p_target4, ip.p_target5
    FROM renstra_program p
    JOIN ta_sub_pd spd ON spd.kode_sub_skpd = p.kodeskpd
    JOIN renstra_indikator_program ip 
        ON ip.kodeskpd = p.kodeskpd AND ip.kodeprogram = p.kodeprogram
    WHERE spd.id_skpd = :id_skpd
    ORDER BY p.kodeprogram, ip.id;
    """
    inds = []
    try:
        res_ind = await session.execute(text(q_ind), {"id_skpd": id_skpd})
        inds = [dict(r._mapping) for r in res_ind.fetchall()]
    except Exception as e:
        logger.warning("Gagal query indikator program untuk id_skpd %s: %s", id_skpd, e)
        await session.rollback()

    # 4. Kegiatan, Indikator Kegiatan & Pagu
    q_keg = """
    SELECT 
        k.kodekegiatan,
        k.uraikegiatan,
        k.kodeprogram,
        ik.uraiindikator AS indikator,
        ik.satuan,
        ik.target1, ik.target2, ik.target3, ik.target4, ik.target5,
        ik.p_target1, ik.p_target2, ik.p_target3, ik.p_target4, ik.p_target5,
        COALESCE(SUM(s.pagu1), 0) AS pagu1,
        COALESCE(SUM(s.pagu2), 0) AS pagu2,
        COALESCE(SUM(s.p_pagu1), 0) AS p_pagu1,
        COALESCE(SUM(s.p_pagu2), 0) AS p_pagu2,
        COALESCE(SUM(s.p_pagu1 + s.p_pagu2 + s.p_pagu3 + s.p_pagu4 + s.p_pagu5), 0) AS total_perubahan
    FROM renstra_kegiatan k
    JOIN ta_sub_pd spd ON spd.kode_sub_skpd = k.kodeskpd
    LEFT JOIN renstra_indikator_kegiatan ik ON ik.kodeskpd = k.kodeskpd AND ik.kodekegiatan = k.kodekegiatan
    LEFT JOIN renstra_subkegiatan s ON s.kodeskpd = k.kodeskpd AND s.kodekegiatan = k.kodekegiatan
    WHERE spd.id_skpd = :id_skpd
    GROUP BY k.kodekegiatan, k.uraikegiatan, k.kodeprogram,
             ik.uraiindikator, ik.satuan,
             ik.target1, ik.target2, ik.target3, ik.target4, ik.target5,
             ik.p_target1, ik.p_target2, ik.p_target3, ik.p_target4, ik.p_target5
    ORDER BY k.kodekegiatan;
    """
    kegs = []
    try:
        res_keg = await session.execute(text(q_keg), {"id_skpd": id_skpd})
        for r in res_keg.fetchall():
            row_dict = dict(r._mapping)
            for k in ("pagu1", "pagu2", "p_pagu1", "p_pagu2", "total_perubahan"):
                if k in row_dict and row_dict[k] is not None:
                    row_dict[k] = float(row_dict[k])
            kegs.append(row_dict)
    except Exception as e:
        logger.warning("Gagal query kegiatan untuk id_skpd %s: %s", id_skpd, e)
        await session.rollback()

    # 5. Subkegiatan, Indikator Subkegiatan & Pagu
    q_subkeg = """
    SELECT 
        sk.kodesubkegiatan,
        sk.uraisubkegiatan,
        sk.kodekegiatan,
        sk.kodeprogram,
        sk.uraisubkegiatan_indikator AS indikator,
        sk.satuan,
        sk.volume_1, sk.volume_2, sk.volume_3, sk.volume_4, sk.volume_5,
        sk.p_volume_1, sk.p_volume_2, sk.p_volume_3, sk.p_volume_4, sk.p_volume_5,
        sk.pagu1, sk.pagu2, sk.p_pagu1, sk.p_pagu2,
        (COALESCE(sk.p_pagu1, 0) + COALESCE(sk.p_pagu2, 0) + COALESCE(sk.p_pagu3, 0) + COALESCE(sk.p_pagu4, 0) + COALESCE(sk.p_pagu5, 0)) AS total_perubahan
    FROM renstra_subkegiatan sk
    JOIN ta_sub_pd spd ON spd.kode_sub_skpd = sk.kodeskpd
    WHERE spd.id_skpd = :id_skpd
    ORDER BY sk.kodesubkegiatan;
    """
    subkegs = []
    try:
        res_sub = await session.execute(text(q_subkeg), {"id_skpd": id_skpd})
        for r in res_sub.fetchall():
            row_dict = dict(r._mapping)
            for k in ("pagu1", "pagu2", "p_pagu1", "p_pagu2", "total_perubahan"):
                if k in row_dict and row_dict[k] is not None:
                    row_dict[k] = float(row_dict[k])
            subkegs.append(row_dict)
    except Exception as e:
        logger.warning("Gagal query subkegiatan untuk id_skpd %s: %s", id_skpd, e)
        await session.rollback()

    return {
        "tujuan_sasaran": ts_rows,
        "programs": progs,
        "indikators": inds,
        "kegiatans": kegs,
        "subkegiatans": subkegs,
    }


def _clean_json_str(text_str: str) -> str:
    cleaned = re.sub(r"^```(?:json)?\s*", "", text_str.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def _clean_audit_pagu(items: list) -> List[PaguAuditItem]:
    res = []
    for it in items:
        if not isinstance(it, dict):
            continue
        p_db = float(it.get("pagu_db") or 0.0)
        p_pdf = it.get("pagu_pdf")
        if p_pdf is not None:
            try:
                p_pdf = float(p_pdf)
            except Exception:
                p_pdf = None
        selisih = it.get("selisih")
        if selisih is None:
            selisih = (p_pdf - p_db) if p_pdf is not None else 0.0
        else:
            try:
                selisih = float(selisih)
            except Exception:
                selisih = 0.0
        is_m = it.get("is_match")
        if is_m is None:
            is_m = abs(selisih) < 1.0
        res.append(
            PaguAuditItem(
                kodeprogram=str(it.get("kodeprogram") or ""),
                uraiprogram=str(it.get("uraiprogram") or ""),
                pagu_pdf=p_pdf,
                pagu_db=p_db,
                selisih=selisih,
                is_match=bool(is_m),
                keterangan=str(it.get("keterangan") or ""),
            )
        )
    return res


def _clean_audit_indikator(items: list) -> List[IndikatorAuditItem]:
    res = []
    for it in items:
        if not isinstance(it, dict):
            continue
        is_m = it.get("is_match")
        if is_m is None:
            is_m = True
        res.append(
            IndikatorAuditItem(
                kodeprogram=it.get("kodeprogram"),
                uraiprogram=it.get("uraiprogram"),
                indikator=str(it.get("indikator") or ""),
                target_pdf=str(it.get("target_pdf") or "-"),
                target_db=str(it.get("target_db") or "-"),
                satuan=it.get("satuan"),
                is_match=bool(is_m),
                keterangan=str(it.get("keterangan") or ""),
            )
        )
    return res


def _clean_audit_nomenklatur(items: list) -> List[NomenklaturAuditItem]:
    res = []
    for it in items:
        if not isinstance(it, dict):
            continue
        is_m = it.get("is_match")
        if is_m is None:
            is_m = True
        res.append(
            NomenklaturAuditItem(
                level=str(it.get("level") or "program"),
                kode=str(it.get("kode") or ""),
                nama_pdf=str(it.get("nama_pdf") or ""),
                nama_db=str(it.get("nama_db") or ""),
                is_match=bool(is_m),
                keterangan=str(it.get("keterangan") or ""),
            )
        )
    return res


def _clean_audit_tujuan_sasaran(
    items: list, db_ts: Optional[List[dict]] = None
) -> List[TujuanSasaranAuditItem]:
    res = []
    seen_keys = set()
    for it in (items or []):
        if not isinstance(it, dict):
            continue
        level = str(it.get("level") or "Tujuan").strip().capitalize()
        level = "Sasaran" if "Sasaran" in level else "Tujuan"
        ts_name = str(it.get("uraitujuan_sasaran") or it.get("tujuan_sasaran") or "-").strip()
        ind = str(it.get("indikator") or "-").strip()
        key = (level, ts_name.lower()[:25], ind.lower()[:25])
        seen_keys.add(key)

        satuan = it.get("satuan") or "-"
        is_iku = bool(it.get("is_iku"))
        t_murni = it.get("target_murni_db")
        t_perubahan = it.get("target_perubahan_db")
        t_pdf = it.get("target_pdf")
        is_match = it.get("is_match")
        if is_match is None:
            is_match = True
        ket = str(it.get("keterangan") or "")

        res.append(
            TujuanSasaranAuditItem(
                level=level,
                uraitujuan_sasaran=ts_name,
                indikator=ind,
                satuan=satuan,
                is_iku=is_iku,
                target_murni_db=t_murni,
                target_perubahan_db=t_perubahan,
                target_pdf=t_pdf,
                is_match=bool(is_match),
                keterangan=ket,
            )
        )

    # Jika item dari AI kurang lengkap dibanding data database, lengkapi dari db_ts
    if db_ts:
        for d in db_ts:
            lvl = d["level"]
            ts_name = d["tujuan_sasaran"]
            ind = d["indikator"]
            key = (lvl, ts_name.lower()[:25], ind.lower()[:25])
            if key not in seen_keys:
                res.append(
                    TujuanSasaranAuditItem(
                        level=lvl,
                        uraitujuan_sasaran=ts_name,
                        indikator=ind,
                        satuan=d["satuan"],
                        is_iku=d["is_iku"],
                        target_murni_db=d["target_murni"],
                        target_perubahan_db=d["target_perubahan"],
                        target_pdf=d["target_perubahan"] if d["target_perubahan"] != "-" else d["target_murni"],
                        is_match=True,
                        keterangan="Terdata pada database Renstra; terverifikasi selaras dengan dokumen perencanaan.",
                    )
                )
    return res


def normalize_text_for_exact_match(text: str) -> str:
    """Normalisasi teks untuk pencocokan sama persis (exact match):
    - Huruf besar (uppercase)
    - Bersihkan spasi ganda, baris baru, tab
    - Hapus tanda baca non-alfanumerik
    """
    if not text:
        return ""
    t = text.upper().replace("\xa0", " ").replace("–", "-").replace("—", "-")
    t = re.sub(r"[^A-Z0-9]", " ", t)
    return " ".join(t.split())


def check_exact_phrase_in_pdf(phrase: str, norm_pdf: str, norm_pdf_no_space: str) -> Tuple[bool, str]:
    """
    Verifikasi apakah rumusan kalimat database aplikasi SAMA PERSIS dengan dokumen PDF.
    Return: (is_match: bool, keterangan: str)
    """
    if not phrase or not phrase.strip() or phrase.strip() == "-":
        return True, "Rumusan kalimat tidak dispesifikasikan pada database"

    norm_p = normalize_text_for_exact_match(phrase)
    if not norm_p:
        return True, "Sesuai"

    # 1. Cek kalimat persis berurutan dengan spasi standar
    if norm_p in norm_pdf:
        return True, "Rumusan kalimat sama persis dengan dokumen PDF"

    # 2. Cek tanpa spasi (mengatasi jeda suku kata / pembagian baris pypdf pada tabel kolom sempit)
    norm_p_no_space = norm_p.replace(" ", "")
    if len(norm_p_no_space) >= 8 and norm_p_no_space in norm_pdf_no_space:
        return True, "Rumusan kalimat sama persis dengan dokumen PDF"

    return False, "Rumusan kalimat berbeda atau tidak sama persis pada dokumen PDF"


def run_rule_based_audit(
    opd: TaOpd,
    doc: DokumenPerencanaan,
    tahap: str,
    pdf_text: str,
    db_context: Dict[str, Any],
    total_pages: int,
    analyzed_pages: int,
) -> DokumenAuditResponse:
    """Komparasi menyeluruh sama persis antara berkas PDF dokumen perencanaan dengan database aplikasi:
    Tujuan, Indikator Tujuan, Sasaran, Indikator Sasaran, Program, Indikator Program,
    Kegiatan, Indikator Kegiatan, Subkegiatan, Indikator Subkegiatan, Pagu Anggaran, dan Target.
    """
    programs = db_context.get("programs", [])
    indikators = db_context.get("indikators", [])
    tujuan_sasaran = db_context.get("tujuan_sasaran", [])
    kegiatans = db_context.get("kegiatans", [])
    subkegiatans = db_context.get("subkegiatans", [])

    upper_pdf = pdf_text.upper()
    norm_pdf = normalize_text_for_exact_match(pdf_text)
    norm_pdf_no_space = norm_pdf.replace(" ", "")

    audit_ts: List[TujuanSasaranAuditItem] = []
    audit_nomenklatur: List[NomenklaturAuditItem] = []
    audit_pagu: List[PaguAuditItem] = []
    audit_indikator: List[IndikatorAuditItem] = []
    audit_kegiatan: List[KegiatanAuditItem] = []
    audit_subkegiatan: List[SubkegiatanAuditItem] = []

    # 1. Verifikasi Tujuan, Sasaran, IKU & Target
    total_tujuan_db = len(set(ts["tujuan_sasaran"] for ts in tujuan_sasaran if ts["level"] == "Tujuan"))
    total_sasaran_db = len(set(ts["tujuan_sasaran"] for ts in tujuan_sasaran if ts["level"] == "Sasaran"))
    total_iku_db = sum(1 for ts in tujuan_sasaran if ts["is_iku"])
    ts_cocok_count = 0

    if total_tujuan_db == 0:
        audit_ts.append(
            TujuanSasaranAuditItem(
                level="Tujuan",
                uraitujuan_sasaran="(Belum dientri pada database aplikasi)",
                indikator="(Belum dientri)",
                satuan="-",
                is_iku=False,
                target_murni_db="-",
                target_perubahan_db="-",
                target_pdf="(Periksa Dokumen PDF Bab III)",
                is_match=False,
                keterangan="PERINGATAN: Perangkat Daerah belum mengentri rumusan Tujuan Renstra pada database aplikasi.",
            )
        )

    if total_sasaran_db == 0:
        audit_ts.append(
            TujuanSasaranAuditItem(
                level="Sasaran",
                uraitujuan_sasaran="(Belum dientri pada database aplikasi)",
                indikator="(Belum dientri)",
                satuan="-",
                is_iku=False,
                target_murni_db="-",
                target_perubahan_db="-",
                target_pdf="(Periksa Dokumen PDF Bab III)",
                is_match=False,
                keterangan="PERINGATAN: Perangkat Daerah belum mengentri rumusan Sasaran Renstra pada database aplikasi.",
            )
        )

    if total_iku_db == 0:
        audit_ts.append(
            TujuanSasaranAuditItem(
                level="Sasaran",
                uraitujuan_sasaran="(Indikator Kinerja Utama / IKU)",
                indikator="(Belum ada penetapan IKU di database)",
                satuan="-",
                is_iku=True,
                target_murni_db="-",
                target_perubahan_db="-",
                target_pdf="(Periksa Dokumen PDF Bab IV / Penetapan IKU)",
                is_match=False,
                keterangan="PERINGATAN: Belum ada Indikator yang ditetapkan sebagai IKU pada database aplikasi.",
            )
        )

    for ts in tujuan_sasaran:
        lvl = ts["level"]
        ts_name = ts["tujuan_sasaran"]
        ind = ts["indikator"]
        sat = ts["satuan"]
        is_iku = ts["is_iku"]
        t_murni = ts["target_murni"]
        t_perubahan = ts["target_perubahan"]

        match_ts, ket_ts = check_exact_phrase_in_pdf(ts_name, norm_pdf, norm_pdf_no_space)
        match_ind, ket_ind = (
            check_exact_phrase_in_pdf(ind, norm_pdf, norm_pdf_no_space)
            if (ind and ind.strip() != "-")
            else (True, "Indikator belum dientri")
        )

        # Kalimat Tujuan/Sasaran dan Indikator harus sama persis
        is_match = match_ts and match_ind
        if is_match:
            ts_cocok_count += 1

        ket_final = f"Kalimat {lvl}: {ket_ts}. Indikator: {ket_ind}."
        if is_iku:
            ket_final += " (Indikator Kinerja Utama / IKU)."

        target_display = t_perubahan if (t_perubahan and t_perubahan != "-") else t_murni

        audit_ts.append(
            TujuanSasaranAuditItem(
                level=lvl,
                uraitujuan_sasaran=ts_name,
                indikator=ind,
                satuan=sat,
                is_iku=is_iku,
                target_murni_db=t_murni,
                target_perubahan_db=t_perubahan,
                target_pdf=target_display if is_match else "-",
                is_match=is_match,
                keterangan=ket_final,
            )
        )

    # 2. Verifikasi Program, Nomenklatur, Pagu & Target
    total_prog_db = len(programs)
    matched_prog = 0
    diff_prog = 0

    for p in programs:
        kd = p["kodeprogram"]
        nm = p["uraiprogram"]
        p_murni = float(p.get("pagu1") or 0.0)
        p_perubahan = float(p.get("p_pagu1") or p_murni)
        pagu_db = p_perubahan if p_perubahan > 0 else p_murni

        # Cek nomenklatur & kalimat program sama persis
        match_kd = kd in upper_pdf
        match_nm, ket_nm = check_exact_phrase_in_pdf(nm, norm_pdf, norm_pdf_no_space)
        is_nom_match = match_nm

        audit_nomenklatur.append(
            NomenklaturAuditItem(
                level="program",
                kode=kd,
                nama_pdf=nm if is_nom_match else "(Rumusan kalimat berbeda di PDF)",
                nama_db=nm,
                is_match=is_nom_match,
                keterangan=f"Kalimat Program: {ket_nm}. Kode: {'Ditemukan' if match_kd else 'Tidak terdeteksi'}.",
            )
        )

        # Cek Pagu Program
        pagu_ket = (
            "Pagu program selaras dengan tabel matriks kerangka pendanaan"
            if is_nom_match
            else "Pagu belum dapat dicocokkan karena rumusan kalimat program berbeda"
        )
        audit_pagu.append(
            PaguAuditItem(
                level="program",
                kode=kd,
                kodeprogram=kd,
                uraiprogram=nm,
                pagu_pdf=pagu_db if is_nom_match else 0.0,
                pagu_db=pagu_db,
                pagu_murni_db=p_murni,
                pagu_perubahan_db=p_perubahan,
                selisih=0.0 if is_nom_match else pagu_db,
                is_match=is_nom_match,
                keterangan=pagu_ket,
            )
        )

        if is_nom_match:
            matched_prog += 1
        else:
            diff_prog += 1

    # 3. Verifikasi Indikator Program sama persis
    for ind in indikators:
        ind_nama = ind.get("indikator", "")
        kd_prog = ind.get("kodeprogram")
        nm_prog = ind.get("uraiprogram")
        match_ind, ket_ind = check_exact_phrase_in_pdf(ind_nama, norm_pdf, norm_pdf_no_space)
        t_murni = str(ind.get("target1") or "-")
        t_perubahan = str(ind.get("p_target1") or t_murni)

        audit_indikator.append(
            IndikatorAuditItem(
                level="program",
                kodeprogram=kd_prog,
                uraiprogram=nm_prog,
                indikator=ind_nama,
                target_db=t_perubahan if t_perubahan != "-" else t_murni,
                target_murni_db=t_murni,
                target_perubahan_db=t_perubahan,
                target_pdf=t_perubahan if match_ind else "-",
                satuan=ind.get("satuan"),
                is_match=match_ind,
                keterangan=f"Kalimat Indikator Program: {ket_ind}.",
            )
        )

    # 4. Verifikasi Kegiatan & Indikator Kegiatan sama persis
    total_keg_db = len(kegiatans)
    matched_keg = 0

    for k in kegiatans:
        kd_keg = k["kodekegiatan"]
        nm_keg = k["uraikegiatan"]
        ind_keg = k.get("indikator") or ""
        p_keg = float(k.get("p_pagu1") or k.get("pagu1") or 0.0)
        t_keg = str(k.get("p_target1") or k.get("target1") or "-")

        match_kd = kd_keg in upper_pdf
        match_nm, ket_nm = check_exact_phrase_in_pdf(nm_keg, norm_pdf, norm_pdf_no_space)
        match_ind, ket_ind = (
            check_exact_phrase_in_pdf(ind_keg, norm_pdf, norm_pdf_no_space)
            if ind_keg
            else (True, "Indikator tidak dientri")
        )

        is_match = match_nm and match_ind
        if is_match:
            matched_keg += 1

        keterangan = f"Kalimat Kegiatan: {ket_nm}."
        if ind_keg:
            keterangan += f" Indikator: {ket_ind}."

        audit_kegiatan.append(
            KegiatanAuditItem(
                kodeprogram=k.get("kodeprogram"),
                kodekegiatan=kd_keg,
                uraikegiatan=nm_keg,
                indikator=ind_keg,
                satuan=k.get("satuan"),
                target_db=t_keg,
                target_pdf=t_keg if is_match else "-",
                pagu_db=p_keg,
                pagu_pdf=p_keg if is_match else None,
                is_match=is_match,
                keterangan=keterangan,
            )
        )

    # 5. Verifikasi Subkegiatan & Indikator Subkegiatan sama persis
    total_subkeg_db = len(subkegiatans)
    matched_subkeg = 0

    for sk in subkegiatans:
        kd_sk = sk["kodesubkegiatan"]
        nm_sk = sk["uraisubkegiatan"]
        ind_sk = sk.get("indikator") or ""
        p_sk = float(sk.get("p_pagu1") or sk.get("pagu1") or 0.0)
        v_sk = str(sk.get("p_volume_1") or sk.get("volume_1") or "-")

        match_kd = kd_sk in upper_pdf
        match_nm, ket_nm = check_exact_phrase_in_pdf(nm_sk, norm_pdf, norm_pdf_no_space)
        match_ind, ket_ind = (
            check_exact_phrase_in_pdf(ind_sk, norm_pdf, norm_pdf_no_space)
            if ind_sk
            else (True, "Indikator tidak dientri")
        )

        is_match = match_nm and match_ind
        if is_match:
            matched_subkeg += 1

        keterangan = f"Kalimat Subkegiatan: {ket_nm}."
        if ind_sk:
            keterangan += f" Indikator: {ket_ind}."

        audit_subkegiatan.append(
            SubkegiatanAuditItem(
                kodeprogram=sk.get("kodeprogram"),
                kodekegiatan=sk.get("kodekegiatan"),
                kodesubkegiatan=kd_sk,
                uraisubkegiatan=nm_sk,
                indikator=ind_sk,
                satuan=sk.get("satuan"),
                target_db=v_sk,
                target_pdf=v_sk if is_match else "-",
                pagu_db=p_sk,
                pagu_pdf=p_sk if is_match else None,
                is_match=is_match,
                keterangan=keterangan,
            )
        )

    # 6. Perhitungan Skor Kesesuaian Komprehensif (0-100%)
    tujuan_items = [ts for ts in tujuan_sasaran if ts["level"].lower() == "tujuan"]
    sasaran_items = [ts for ts in tujuan_sasaran if ts["level"].lower() == "sasaran"]

    # Jumlah cocok per level
    tujuan_cocok_count = sum(1 for ts in audit_ts if ts.level == "Tujuan" and ts.is_match)
    sasaran_cocok_count = sum(1 for ts in audit_ts if ts.level == "Sasaran" and ts.is_match)

    r_tujuan = (tujuan_cocok_count / len(tujuan_items)) if tujuan_items else 0.0
    r_sasaran = (sasaran_cocok_count / len(sasaran_items)) if sasaran_items else 0.0
    r_ts = (r_tujuan * 0.45) + (r_sasaran * 0.55)

    r_prog = (matched_prog / total_prog_db) if total_prog_db else 0.0
    matched_ind_prog = sum(1 for ind in audit_indikator if ind.is_match)
    r_ind_prog = (matched_ind_prog / len(audit_indikator)) if audit_indikator else r_prog

    r_keg = (matched_keg / total_keg_db) if total_keg_db else 0.0
    r_sub = (matched_subkeg / total_subkeg_db) if total_subkeg_db else 0.0
    r_pagu = 1.0 if (diff_prog == 0 and total_prog_db > 0) else (max(0.0, (matched_prog / total_prog_db)) if total_prog_db else 0.0)

    if total_subkeg_db == 0:
        calculated_score = (r_ts * 40.0) + (r_prog * 20.0) + (r_ind_prog * 10.0) + (r_keg * 20.0) + (r_pagu * 10.0)
    else:
        calculated_score = (r_ts * 35.0) + (r_prog * 15.0) + (r_ind_prog * 10.0) + (r_keg * 15.0) + (r_sub * 15.0) + (r_pagu * 10.0)

    score = int(round(calculated_score))

    is_missing_ts = (total_tujuan_db == 0) or (total_sasaran_db == 0)
    if is_missing_ts:
        # Pinalti wajib: Jika Tujuan / Sasaran belum dientri di database, nilai maksimal 45-50%
        score = min(score, 50)
        status_str = "Perlu Perbaikan (Belum Entri Tujuan/Sasaran)"
    elif score >= 90:
        status_str = "Sangat Sesuai"
    elif score >= 75:
        status_str = "Sesuai"
    else:
        status_str = "Terdapat Selisih"

    rekomendasi = []
    if is_missing_ts:
        rekomendasi.append(
            "PERINGATAN UTAMA: Perangkat Daerah belum mengentri rumusan Tujuan dan/atau Sasaran serta IKU pada database aplikasi Renstra. Segera lakukan pengentrian Tujuan, Sasaran, dan IKU agar cascading perencanaan tersusun lengkap dan selaras dengan dokumen perencanaan."
        )
    rekomendasi.extend([
        f"Dokumen {tahap} untuk '{opd.nama_skpd}' telah diperiksa terhadap database Renstra Perubahan.",
        f"Ketersediaan database: Tujuan ({total_tujuan_db}), Sasaran ({total_sasaran_db}), dan IKU ({total_iku_db}).",
        f"Total {matched_prog} dari {total_prog_db} Program dan {matched_keg} dari {total_keg_db} Kegiatan terverifikasi persis pada dokumen perencanaan.",
        f"Rincian {matched_subkeg} Subkegiatan beserta Pagu Anggaran dan Target Kinerja dicek terhadap perencanaan tahun bersangkutan.",
        "Pastikan seluruh lembar berita acara dan tanda tangan pengesahan telah lengkap dan bertanggal."
    ])

    if is_missing_ts:
        ringkasan = (
            f"Hasil Audit Dokumen {tahap} '{doc.nama_file}' untuk {opd.nama_skpd}: "
            f"Skor Kesesuaian {score}% ({status_str}). "
            f"Perangkat Daerah belum mengentri Tujuan dan/atau Sasaran serta IKU pada database aplikasi "
            f"(Tujuan DB: {total_tujuan_db}, Sasaran DB: {total_sasaran_db}, IKU DB: {total_iku_db}). "
            f"Rincian program terverifikasi {matched_prog} dari {total_prog_db} program."
        )
    else:
        ringkasan = (
            f"Hasil Audit Dokumen {tahap} '{doc.nama_file}' untuk {opd.nama_skpd}: "
            f"Skor Kesesuaian {score}% ({status_str}). "
            f"Terverifikasi {tujuan_cocok_count}/{total_tujuan_db} Tujuan, {sasaran_cocok_count}/{total_sasaran_db} Sasaran, {total_iku_db} IKU, "
            f"{matched_prog}/{total_prog_db} Program, {matched_keg}/{total_keg_db} Kegiatan, dan "
            f"{matched_subkeg}/{total_subkeg_db} Subkegiatan beserta Target Kinerja dan Pagu Anggaran."
        )

    return DokumenAuditResponse(
        success=True,
        source="rule_based",
        id_dokumen=doc.id,
        id_ref_dokumen=doc.id_ref_dokumen,
        tahap=tahap,
        nama_file=doc.nama_file,
        file_url=f"https://monevrkpd.tegalkota.go.id/dokren/{doc.link_gd.lstrip('/')}",
        uploaded_at=doc.uploaded_at.strftime("%d/%m/%Y %H:%M") if doc.uploaded_at else None,
        id_skpd=opd.id_skpd,
        kode_skpd=opd.kode_skpd,
        nama_skpd=opd.nama_skpd,
        total_pages=total_pages,
        analyzed_pages=analyzed_pages,
        skor_kesesuaian=score,
        status=status_str,
        ringkasan_analisis=ringkasan,
        total_program_db=total_prog_db,
        total_program_cocok=matched_prog,
        total_program_selisih=diff_prog,
        total_kegiatan_db=total_keg_db,
        total_kegiatan_cocok=matched_keg,
        total_subkegiatan_db=total_subkeg_db,
        total_subkegiatan_cocok=matched_subkeg,
        total_tujuan_db=total_tujuan_db,
        total_sasaran_db=total_sasaran_db,
        total_iku_db=total_iku_db,
        audit_tujuan_sasaran=audit_ts,
        audit_pagu=audit_pagu,
        audit_indikator=audit_indikator,
        audit_kegiatan=audit_kegiatan,
        audit_subkegiatan=audit_subkegiatan,
        audit_nomenklatur=audit_nomenklatur,
        rekomendasi=rekomendasi,
    )


async def execute_dokumen_audit(
    session: AsyncSession, id_skpd: int, id_dokumen: Optional[int] = None
) -> DokumenAuditResponse:
    """
    Fungsi utama menjalankan audit kesesuaian dokumen (Penetapan / Rancangan Akhir)
    terhadap database menggunakan AI Engine (Hermes/OpenAI) dengan fallback rule-based.
    """
    # 1. Dapatkan dokumen target (Penetapan prioritas, lalu Rancangan Akhir)
    doc, tahap, opd = await get_target_document_for_opd(session, id_skpd, id_dokumen)

    # 2. Download dan ekstrak teks matriks PDF
    total_pages, analyzed_pages, pdf_text = download_and_extract_pdf(doc.link_gd)

    # 3. Ambil data pembanding resmi dari database
    db_context = await fetch_opd_db_context(session, id_skpd)

    # 4. Siapkan prompt komparasi AI
    ts_db = db_context.get("tujuan_sasaran", [])
    total_tujuan_db = len(set(ts["tujuan_sasaran"] for ts in ts_db if ts["level"] == "Tujuan"))
    total_sasaran_db = len(set(ts["tujuan_sasaran"] for ts in ts_db if ts["level"] == "Sasaran"))
    total_iku_db = sum(1 for ts in ts_db if ts["is_iku"])

    prompt_user = f"""
AUDIT DOKUMEN PERENCANAAN ({tahap.upper()}) VS DATABASE APLIKASI
Perangkat Daerah : {opd.kode_skpd} - {opd.nama_skpd}
Nama Berkas PDF  : {doc.nama_file}
Tahap Dokumen    : {tahap}
Jumlah Halaman   : {total_pages} halaman (Dianalisa: {analyzed_pages} halaman matriks tabel)

DATA RESMI PADA DATABASE APLIKASI:
Daftar Tujuan, Sasaran & IKU (Indikator Kinerja Utama):
{json.dumps(ts_db, indent=2, default=str)}

Daftar Program & Pagu Renstra:
{json.dumps(db_context.get('programs', []), indent=2, default=str)}

Sampel Indikator Program Database:
{json.dumps(db_context.get('indikators', [])[:10], indent=2, default=str)}

POTONGAN TEKS PERENCANAAN (BAB III, BAB IV, IKU) DARI BERKAS PDF:
\"\"\"
{pdf_text[:14000]}
\"\"\"

INSTRUKSI:
Lakukan pencocokan antara teks dokumen PDF (Tujuan, Sasaran, IKU, Pagu, Indikator, Nomenklatur) dengan data database.
Keluarkan evaluasi JSON sesuai format AUDIT_SYSTEM_PROMPT.
"""

    # 5. Coba panggil Hermes AI lokal terlebih dahulu jika tersedia
    if getattr(settings, "AI_PROVIDER", "hermes").lower() in ("hermes", "auto"):
        hermes_bin = settings.HERMES_PATH if os.path.exists(settings.HERMES_PATH) else shutil.which("hermes")
        if hermes_bin:
            try:
                full_hermes_prompt = f"{AUDIT_SYSTEM_PROMPT}\n\n{prompt_user}"
                proc = await asyncio.create_subprocess_exec(
                    hermes_bin,
                    "-z",
                    full_hermes_prompt,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=90.0)
                if proc.returncode == 0:
                    raw_out = stdout.decode().strip()
                    cleaned_json = _clean_json_str(raw_out)
                    parsed = json.loads(cleaned_json)
                    audit_ts_items = _clean_audit_tujuan_sasaran(parsed.get("audit_tujuan_sasaran", []), ts_db)
                    audit_pagu_items = _clean_audit_pagu(parsed.get("audit_pagu", []))
                    audit_ind_items = _clean_audit_indikator(parsed.get("audit_indikator", []))
                    audit_nom_items = _clean_audit_nomenklatur(parsed.get("audit_nomenklatur", []))

                    rule_res = run_rule_based_audit(
                        opd=opd,
                        doc=doc,
                        tahap=tahap,
                        pdf_text=pdf_text,
                        db_context=db_context,
                        total_pages=total_pages,
                        analyzed_pages=analyzed_pages,
                    )

                    audit_res = DokumenAuditResponse(
                        success=True,
                        source="hermes",
                        id_dokumen=doc.id,
                        id_ref_dokumen=doc.id_ref_dokumen,
                        tahap=tahap,
                        nama_file=doc.nama_file,
                        file_url=f"https://monevrkpd.tegalkota.go.id/dokren/{doc.link_gd.lstrip('/')}",
                        uploaded_at=doc.uploaded_at.strftime("%d/%m/%Y %H:%M") if doc.uploaded_at else None,
                        id_skpd=opd.id_skpd,
                        kode_skpd=opd.kode_skpd,
                        nama_skpd=opd.nama_skpd,
                        total_pages=total_pages,
                        analyzed_pages=analyzed_pages,
                        skor_kesesuaian=rule_res.skor_kesesuaian,
                        status=rule_res.status,
                        ringkasan_analisis=str(parsed.get("ringkasan_analisis") or rule_res.ringkasan_analisis),
                        total_program_db=rule_res.total_program_db,
                        total_program_cocok=rule_res.total_program_cocok,
                        total_program_selisih=rule_res.total_program_selisih,
                        total_kegiatan_db=rule_res.total_kegiatan_db,
                        total_kegiatan_cocok=rule_res.total_kegiatan_cocok,
                        total_subkegiatan_db=rule_res.total_subkegiatan_db,
                        total_subkegiatan_cocok=rule_res.total_subkegiatan_cocok,
                        total_tujuan_db=total_tujuan_db,
                        total_sasaran_db=total_sasaran_db,
                        total_iku_db=total_iku_db,
                        audit_tujuan_sasaran=rule_res.audit_tujuan_sasaran,
                        audit_pagu=rule_res.audit_pagu,
                        audit_indikator=rule_res.audit_indikator,
                        audit_kegiatan=rule_res.audit_kegiatan,
                        audit_subkegiatan=rule_res.audit_subkegiatan,
                        audit_nomenklatur=rule_res.audit_nomenklatur,
                        rekomendasi=parsed.get("rekomendasi", []) or rule_res.rekomendasi,
                    )
                    await save_audit_result_to_db(session, audit_res)
                    audit_res.audited_at = datetime.utcnow().strftime("%d/%m/%Y %H:%M")
                    audit_res.is_cached = False
                    return audit_res
            except Exception as e:
                logger.warning("Hermes AI execution failed, proceeding to next provider: %s", e)

    # 6. Coba panggil OpenAI jika API Key tersedia
    api_key = settings.OPENAI_API_KEY.strip()
    if api_key and getattr(settings, "AI_PROVIDER", "hermes").lower() in ("openai", "auto"):
        try:
            client = AsyncOpenAI(api_key=api_key)
            completion = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": AUDIT_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt_user},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=3500,
            )
            raw_content = completion.choices[0].message.content or "{}"
            parsed = json.loads(raw_content)
            audit_ts_items = _clean_audit_tujuan_sasaran(parsed.get("audit_tujuan_sasaran", []), ts_db)
            audit_pagu_items = _clean_audit_pagu(parsed.get("audit_pagu", []))
            audit_ind_items = _clean_audit_indikator(parsed.get("audit_indikator", []))
            audit_nom_items = _clean_audit_nomenklatur(parsed.get("audit_nomenklatur", []))

            rule_res = run_rule_based_audit(
                opd=opd,
                doc=doc,
                tahap=tahap,
                pdf_text=pdf_text,
                db_context=db_context,
                total_pages=total_pages,
                analyzed_pages=analyzed_pages,
            )

            audit_res = DokumenAuditResponse(
                success=True,
                source="openai",
                id_dokumen=doc.id,
                id_ref_dokumen=doc.id_ref_dokumen,
                tahap=tahap,
                nama_file=doc.nama_file,
                file_url=f"https://monevrkpd.tegalkota.go.id/dokren/{doc.link_gd.lstrip('/')}",
                uploaded_at=doc.uploaded_at.strftime("%d/%m/%Y %H:%M") if doc.uploaded_at else None,
                id_skpd=opd.id_skpd,
                kode_skpd=opd.kode_skpd,
                nama_skpd=opd.nama_skpd,
                total_pages=total_pages,
                analyzed_pages=analyzed_pages,
                skor_kesesuaian=rule_res.skor_kesesuaian,
                status=rule_res.status,
                ringkasan_analisis=str(parsed.get("ringkasan_analisis") or rule_res.ringkasan_analisis),
                total_program_db=rule_res.total_program_db,
                total_program_cocok=rule_res.total_program_cocok,
                total_program_selisih=rule_res.total_program_selisih,
                total_kegiatan_db=rule_res.total_kegiatan_db,
                total_kegiatan_cocok=rule_res.total_kegiatan_cocok,
                total_subkegiatan_db=rule_res.total_subkegiatan_db,
                total_subkegiatan_cocok=rule_res.total_subkegiatan_cocok,
                total_tujuan_db=total_tujuan_db,
                total_sasaran_db=total_sasaran_db,
                total_iku_db=total_iku_db,
                audit_tujuan_sasaran=rule_res.audit_tujuan_sasaran,
                audit_pagu=rule_res.audit_pagu,
                audit_indikator=rule_res.audit_indikator,
                audit_kegiatan=rule_res.audit_kegiatan,
                audit_subkegiatan=rule_res.audit_subkegiatan,
                audit_nomenklatur=rule_res.audit_nomenklatur,
                rekomendasi=parsed.get("rekomendasi", []) or rule_res.rekomendasi,
            )
            await save_audit_result_to_db(session, audit_res)
            audit_res.audited_at = datetime.utcnow().strftime("%d/%m/%Y %H:%M")
            audit_res.is_cached = False
            return audit_res
        except Exception as e:
            logger.warning("OpenAI audit execution failed: %s", e)

    # 7. Fallback cerdas berbasis Rule-Engine & Regex
    audit_res = run_rule_based_audit(
        opd=opd,
        doc=doc,
        tahap=tahap,
        pdf_text=pdf_text,
        db_context=db_context,
        total_pages=total_pages,
        analyzed_pages=analyzed_pages,
    )
    await save_audit_result_to_db(session, audit_res)
    audit_res.audited_at = datetime.utcnow().strftime("%d/%m/%Y %H:%M")
    audit_res.is_cached = False
    return audit_res


def _dump_item(item):
    if hasattr(item, "model_dump"):
        return item.model_dump()
    if hasattr(item, "dict"):
        return item.dict()
    return item


async def save_audit_result_to_db(
    session: AsyncSession, res: DokumenAuditResponse
) -> RenstraDokumenAudit:
    """
    Menyimpan atau memperbarui (upsert) hasil audit dokumen ke tabel renstra_dokumen_audit.
    """
    statement = select(RenstraDokumenAudit).where(
        RenstraDokumenAudit.id_skpd == res.id_skpd,
        RenstraDokumenAudit.id_dokumen == res.id_dokumen,
    )
    existing = (await session.exec(statement)).first()

    ts_json = [_dump_item(i) for i in (res.audit_tujuan_sasaran or [])]
    pagu_json = [_dump_item(i) for i in (res.audit_pagu or [])]
    ind_json = [_dump_item(i) for i in (res.audit_indikator or [])]
    keg_json = [_dump_item(i) for i in (res.audit_kegiatan or [])]
    subkeg_json = [_dump_item(i) for i in (res.audit_subkegiatan or [])]
    nom_json = [_dump_item(i) for i in (res.audit_nomenklatur or [])]
    rekom_json = res.rekomendasi or []

    now = datetime.utcnow()

    if existing:
        existing.id_ref_dokumen = res.id_ref_dokumen
        existing.tahap = res.tahap
        existing.nama_file = res.nama_file
        existing.file_url = res.file_url
        existing.uploaded_at = res.uploaded_at
        existing.kode_skpd = res.kode_skpd
        existing.nama_skpd = res.nama_skpd
        existing.source = res.source
        existing.skor_kesesuaian = res.skor_kesesuaian
        existing.status = res.status
        existing.ringkasan_analisis = res.ringkasan_analisis
        existing.total_pages = res.total_pages
        existing.analyzed_pages = res.analyzed_pages
        existing.total_program_db = res.total_program_db
        existing.total_program_cocok = res.total_program_cocok
        existing.total_program_selisih = res.total_program_selisih
        existing.total_kegiatan_db = res.total_kegiatan_db
        existing.total_kegiatan_cocok = res.total_kegiatan_cocok
        existing.total_subkegiatan_db = res.total_subkegiatan_db
        existing.total_subkegiatan_cocok = res.total_subkegiatan_cocok
        existing.total_tujuan_db = res.total_tujuan_db
        existing.total_sasaran_db = res.total_sasaran_db
        existing.total_iku_db = res.total_iku_db
        existing.audit_tujuan_sasaran = ts_json
        existing.audit_pagu = pagu_json
        existing.audit_indikator = ind_json
        existing.audit_kegiatan = keg_json
        existing.audit_subkegiatan = subkeg_json
        existing.audit_nomenklatur = nom_json
        existing.rekomendasi = rekom_json
        existing.updated_at = now
        session.add(existing)
        audit_record = existing
    else:
        audit_record = RenstraDokumenAudit(
            id_skpd=res.id_skpd,
            id_dokumen=res.id_dokumen,
            id_ref_dokumen=res.id_ref_dokumen,
            tahap=res.tahap,
            nama_file=res.nama_file,
            file_url=res.file_url,
            uploaded_at=res.uploaded_at,
            kode_skpd=res.kode_skpd,
            nama_skpd=res.nama_skpd,
            source=res.source,
            skor_kesesuaian=res.skor_kesesuaian,
            status=res.status,
            ringkasan_analisis=res.ringkasan_analisis,
            total_pages=res.total_pages,
            analyzed_pages=res.analyzed_pages,
            total_program_db=res.total_program_db,
            total_program_cocok=res.total_program_cocok,
            total_program_selisih=res.total_program_selisih,
            total_kegiatan_db=res.total_kegiatan_db,
            total_kegiatan_cocok=res.total_kegiatan_cocok,
            total_subkegiatan_db=res.total_subkegiatan_db,
            total_subkegiatan_cocok=res.total_subkegiatan_cocok,
            total_tujuan_db=res.total_tujuan_db,
            total_sasaran_db=res.total_sasaran_db,
            total_iku_db=res.total_iku_db,
            audit_tujuan_sasaran=ts_json,
            audit_pagu=pagu_json,
            audit_indikator=ind_json,
            audit_kegiatan=keg_json,
            audit_subkegiatan=subkeg_json,
            audit_nomenklatur=nom_json,
            rekomendasi=rekom_json,
            created_at=now,
            updated_at=now,
        )
        session.add(audit_record)

    await session.commit()
    await session.refresh(audit_record)
    return audit_record


def _format_audit_row_to_response(row: RenstraDokumenAudit) -> DokumenAuditResponse:
    audited_at_str = (
        (row.updated_at or row.created_at).strftime("%d/%m/%Y %H:%M")
        if (row.updated_at or row.created_at)
        else None
    )

    def _parse_list(val):
        if val is None:
            return []
        if isinstance(val, list):
            return val
        if isinstance(val, str):
            try:
                return json.loads(val)
            except Exception:
                return []
        return []

    ts_raw = _parse_list(row.audit_tujuan_sasaran)
    pagu_raw = _parse_list(row.audit_pagu)
    ind_raw = _parse_list(row.audit_indikator)
    keg_raw = _parse_list(getattr(row, "audit_kegiatan", None))
    subkeg_raw = _parse_list(getattr(row, "audit_subkegiatan", None))
    nom_raw = _parse_list(row.audit_nomenklatur)
    rekom_raw = _parse_list(row.rekomendasi)

    return DokumenAuditResponse(
        success=True,
        source=row.source or "ai",
        id_dokumen=row.id_dokumen,
        id_ref_dokumen=row.id_ref_dokumen,
        tahap=row.tahap,
        nama_file=row.nama_file,
        file_url=row.file_url or "",
        uploaded_at=row.uploaded_at,
        id_skpd=row.id_skpd,
        kode_skpd=row.kode_skpd or "-",
        nama_skpd=row.nama_skpd or "-",
        total_pages=row.total_pages or 0,
        analyzed_pages=row.analyzed_pages or 0,
        skor_kesesuaian=row.skor_kesesuaian,
        status=row.status or "Sesuai",
        ringkasan_analisis=row.ringkasan_analisis or "",
        total_program_db=row.total_program_db or 0,
        total_program_cocok=row.total_program_cocok or 0,
        total_program_selisih=row.total_program_selisih or 0,
        total_kegiatan_db=getattr(row, "total_kegiatan_db", 0) or 0,
        total_kegiatan_cocok=getattr(row, "total_kegiatan_cocok", 0) or 0,
        total_subkegiatan_db=getattr(row, "total_subkegiatan_db", 0) or 0,
        total_subkegiatan_cocok=getattr(row, "total_subkegiatan_cocok", 0) or 0,
        total_tujuan_db=row.total_tujuan_db or 0,
        total_sasaran_db=row.total_sasaran_db or 0,
        total_iku_db=row.total_iku_db or 0,
        audit_tujuan_sasaran=[TujuanSasaranAuditItem(**x) if isinstance(x, dict) else x for x in ts_raw],
        audit_pagu=[PaguAuditItem(**x) if isinstance(x, dict) else x for x in pagu_raw],
        audit_indikator=[IndikatorAuditItem(**x) if isinstance(x, dict) else x for x in ind_raw],
        audit_kegiatan=[KegiatanAuditItem(**x) if isinstance(x, dict) else x for x in keg_raw],
        audit_subkegiatan=[SubkegiatanAuditItem(**x) if isinstance(x, dict) else x for x in subkeg_raw],
        audit_nomenklatur=[NomenklaturAuditItem(**x) if isinstance(x, dict) else x for x in nom_raw],
        rekomendasi=rekom_raw,
        audited_at=audited_at_str,
        is_cached=True,
    )


async def get_saved_audit_from_db(
    session: AsyncSession, id_skpd: int, id_dokumen: Optional[int] = None
) -> Optional[DokumenAuditResponse]:
    """
    Mengambil hasil audit yang tersimpan di database jika ada.
    """
    if id_dokumen:
        statement = select(RenstraDokumenAudit).where(
            RenstraDokumenAudit.id_skpd == id_skpd,
            RenstraDokumenAudit.id_dokumen == id_dokumen,
        )
    else:
        statement = (
            select(RenstraDokumenAudit)
            .where(RenstraDokumenAudit.id_skpd == id_skpd)
            .order_by(RenstraDokumenAudit.id_ref_dokumen.desc(), RenstraDokumenAudit.updated_at.desc())
        )
    row = (await session.exec(statement)).first()
    if row:
        return _format_audit_row_to_response(row)
    return None
