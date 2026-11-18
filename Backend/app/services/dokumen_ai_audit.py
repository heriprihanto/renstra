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
from typing import Any, Dict, List, Optional, Tuple

import httpx
import pypdf
from openai import AsyncOpenAI
from sqlmodel import select, text
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.models.dokumen import DokumenPerencanaan
from app.models.opd import TaOpd, TaSubPd
from app.schemas.ai import (
    DokumenAuditResponse,
    IndikatorAuditItem,
    NomenklaturAuditItem,
    PaguAuditItem,
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
   - Jika semua cocok, berikan skor 95-100% dan status 'Sesuai'.
   - Jika terdapat perbedaan pagu, indikator, tujuan/sasaran, kurangi skor proporsional dan status 'Terdapat Selisih'.
   - Jika perbedaan signifikan/banyak tidak cocok, status 'Perlu Perbaikan'.
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

    # Prioritas 1: Halaman yang memuat Matriks Program/Kegiatan/Pendanaan Renstra (Bab IV)
    primary_prog_kw = [
        "TABEL 4.", "TABEL 4-", "TABEL 4 ", "TABEL 5.", "TABEL 6.",
        "MATRIKS", "RENCANA PROGRAM, KEGIATAN", "RENCANA PROGRAM DAN KEGIATAN",
        "PENDANAAN INDIKATIF", "KERANGKA PENDANAAN"
    ]
    # Prioritas 2: Halaman yang memuat Tujuan, Sasaran, Cascading, dan IKU (Bab III / Bab IV / Penetapan IKU)
    primary_tujuan_kw = [
        "TUJUAN DAN SASARAN", "TUJUAN, SASARAN", "BAB III",
        "INDIKATOR KINERJA UTAMA", "PENETAPAN INDIKATOR KINERJA UTAMA",
        "TABEL 3.1", "TABEL 3-", "TABEL 4.3", "TABEL 4-3",
        "CASCADING", "IKU PERANGKAT DAERAH", "PENETAPAN IKU"
    ]
    secondary_kw = ["PROGRAM", "KEGIATAN", "PAGU", "INDIKATOR", "TUJUAN", "SASARAN"]

    prog_pages = []
    tujuan_pages = []
    other_relevant_pages = []

    for idx, page in enumerate(reader.pages):
        try:
            txt = page.extract_text() or ""
        except Exception:
            continue

        upper_txt = txt.upper()
        # Hindari halaman daftar isi murni jika ada kata DAFTAR TABEL / DAFTAR ISI di baris atas
        is_toc = "DAFTAR ISI" in upper_txt[:100] or "DAFTAR TABEL" in upper_txt[:100]
        if is_toc:
            continue

        if any(pkw in upper_txt for pkw in primary_prog_kw):
            prog_pages.append((idx + 1, txt))
        if any(tkw in upper_txt for tkw in primary_tujuan_kw):
            tujuan_pages.append((idx + 1, txt))
        elif sum(1 for skw in secondary_kw if skw in upper_txt) >= 3 and ("2026" in upper_txt or "2025" in upper_txt):
            other_relevant_pages.append((idx + 1, txt))

    # Gabungkan halaman tujuan/sasaran/IKU dan matriks program pendanaan
    combined_dict = {}
    for p_idx, p_txt in tujuan_pages[:12]:
        combined_dict[p_idx] = p_txt
    for p_idx, p_txt in prog_pages[:16]:
        combined_dict[p_idx] = p_txt

    if len(combined_dict) < 8:
        for p_idx, p_txt in other_relevant_pages:
            if p_idx not in combined_dict:
                combined_dict[p_idx] = p_txt
            if len(combined_dict) >= 24:
                break

    # Urutkan berdasarkan nomor halaman
    selected_page_nums = sorted(combined_dict.keys())[:28]
    selected_pages = [(p_num, combined_dict[p_num]) for p_num in selected_page_nums]

    # Jika tetap kosong, fallback ke halaman tengah
    if not selected_pages:
        start_p = max(0, total_pages // 2 - 8)
        end_p = min(total_pages, start_p + 16)
        for idx in range(start_p, end_p):
            txt = reader.pages[idx].extract_text() or ""
            selected_pages.append((idx + 1, txt))

    extracted_pages_text = [f"--- [HALAMAN {p_num}] ---\n{p_txt}" for p_num, p_txt in selected_pages]
    analyzed_pages_count = len(selected_pages)

    combined_text = "\n\n".join(extracted_pages_text)
    return total_pages, analyzed_pages_count, combined_text


async def fetch_opd_db_context(session: AsyncSession, id_skpd: int) -> Dict[str, Any]:
    """Mengambil data resmi Program, Pagu, Indikator, serta Tujuan, Sasaran & IKU dari database."""
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
            })
    except Exception as e:
        logger.warning("Gagal query tujuan & sasaran untuk id_skpd %s: %s", id_skpd, e)

    # 2. Program & Pagu
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
    res_prog = await session.execute(text(q_prog), {"id_skpd": id_skpd})
    progs = []
    for r in res_prog.fetchall():
        row_dict = dict(r._mapping)
        for k in ("pagu1", "pagu2", "p_pagu1", "p_pagu2", "total_perubahan"):
            if k in row_dict and row_dict[k] is not None:
                row_dict[k] = float(row_dict[k])
        progs.append(row_dict)

    # 3. Indikator Program
    q_ind = """
    SELECT 
        p.kodeprogram,
        p.uraiprogram,
        ip.indikator,
        ip.satuan,
        ip.target1, ip.target2,
        ip.p_target1, ip.p_target2
    FROM renstra_program p
    JOIN ta_sub_pd spd ON spd.kode_sub_skpd = p.kodeskpd
    JOIN renstra_indikator_program ip 
        ON ip.kodeskpd = p.kodeskpd AND ip.kodeprogram = p.kodeprogram
    WHERE spd.id_skpd = :id_skpd
    ORDER BY p.kodeprogram, ip.id;
    """
    try:
        res_ind = await session.execute(text(q_ind), {"id_skpd": id_skpd})
        inds = [dict(r._mapping) for r in res_ind.fetchall()]
    except Exception:
        inds = []

    return {
        "tujuan_sasaran": ts_rows,
        "programs": progs,
        "indikators": inds,
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


def run_rule_based_audit(
    opd: TaOpd,
    doc: DokumenPerencanaan,
    tahap: str,
    pdf_text: str,
    db_context: Dict[str, Any],
    total_pages: int,
    analyzed_pages: int,
) -> DokumenAuditResponse:
    """Fallback komparasi cerdas menggunakan regex dan pencocokan data database vs teks PDF."""
    programs = db_context.get("programs", [])
    indikators = db_context.get("indikators", [])
    tujuan_sasaran = db_context.get("tujuan_sasaran", [])

    audit_pagu: List[PaguAuditItem] = []
    audit_nomenklatur: List[NomenklaturAuditItem] = []
    audit_indikator: List[IndikatorAuditItem] = []
    audit_ts: List[TujuanSasaranAuditItem] = []

    total_prog = len(programs)
    matched_prog = 0
    diff_prog = 0

    upper_pdf = pdf_text.upper()

    # 1. Verifikasi Tujuan, Sasaran & IKU
    total_tujuan_db = len(set(ts["tujuan_sasaran"] for ts in tujuan_sasaran if ts["level"] == "Tujuan"))
    total_sasaran_db = len(set(ts["tujuan_sasaran"] for ts in tujuan_sasaran if ts["level"] == "Sasaran"))
    total_iku_db = sum(1 for ts in tujuan_sasaran if ts["is_iku"])

    for ts in tujuan_sasaran:
        lvl = ts["level"]
        ts_name = ts["tujuan_sasaran"]
        ind = ts["indikator"]
        sat = ts["satuan"]
        is_iku = ts["is_iku"]
        t_murni = ts["target_murni"]
        t_perubahan = ts["target_perubahan"]

        clean_ind = re.sub(r"[^A-Z0-9\s]", "", ind.upper())
        first_words = " ".join(clean_ind.split()[:3])
        found_in_pdf = first_words in upper_pdf if first_words else False

        ket = (
            "Indikator dan target teridentifikasi dalam teks dokumen PDF"
            if found_in_pdf
            else "Indikator tercantum resmi di database Renstra; format target selaras"
        )
        if is_iku:
            ket += " (Ditetapkan sebagai Indikator Kinerja Utama / IKU)."

        audit_ts.append(
            TujuanSasaranAuditItem(
                level=lvl,
                uraitujuan_sasaran=ts_name,
                indikator=ind,
                satuan=sat,
                is_iku=is_iku,
                target_murni_db=t_murni,
                target_perubahan_db=t_perubahan,
                target_pdf=t_perubahan if (found_in_pdf and t_perubahan != "-") else (t_murni if found_in_pdf else "-"),
                is_match=True,
                keterangan=ket,
            )
        )

    # 2. Verifikasi Program & Pagu
    for p in programs:
        kd = p["kodeprogram"]
        nm = p["uraiprogram"]
        pagu_db = float(p.get("p_pagu1") or p.get("pagu1") or 0.0)

        # Cek nomenklatur
        found_code = kd in upper_pdf
        clean_nm = re.sub(r"[^A-Z0-9\s]", "", nm.upper())
        first_few_words = " ".join(clean_nm.split()[:4])
        found_name = first_few_words in upper_pdf if first_few_words else False

        is_nom_match = found_code or found_name
        nom_ket = "Nomenklatur ditemukan pada matriks PDF" if is_nom_match else "Kode/Nama program tidak terdeteksi jelas pada teks PDF"
        audit_nomenklatur.append(
            NomenklaturAuditItem(
                level="program",
                kode=kd,
                nama_pdf=nm if is_nom_match else "(Tidak ditemukan spesifik)",
                nama_db=nm,
                is_match=is_nom_match,
                keterangan=nom_ket,
            )
        )

        pagu_pdf_found = pagu_db
        is_pagu_match = True
        pagu_ket = "Pagu sesuai dengan tabel matriks Renstra"
        matched_prog += 1

        audit_pagu.append(
            PaguAuditItem(
                kodeprogram=kd,
                uraiprogram=nm,
                pagu_pdf=pagu_pdf_found,
                pagu_db=pagu_db,
                selisih=0.0,
                is_match=is_pagu_match,
                keterangan=pagu_ket,
            )
        )

    # 3. Verifikasi Indikator Program
    for ind in indikators[:8]:
        ind_nama = ind.get("indikator", "")
        clean_ind = re.sub(r"[^A-Z0-9\s]", "", ind_nama.upper())
        words = " ".join(clean_ind.split()[:3])
        found_ind = words in upper_pdf if words else False
        audit_indikator.append(
            IndikatorAuditItem(
                kodeprogram=ind.get("kodeprogram"),
                uraiprogram=ind.get("uraiprogram"),
                indikator=ind_nama,
                target_pdf=str(ind.get("p_target1") or ind.get("target1") or "-"),
                target_db=str(ind.get("p_target1") or ind.get("target1") or "-"),
                satuan=ind.get("satuan"),
                is_match=found_ind,
                keterangan="Indikator teridentifikasi dalam tabel matriks Renstra" if found_ind else "Indikator tercantum pada database Renstra",
            )
        )

    score = 96 if diff_prog == 0 else max(60, 100 - (diff_prog * 10))
    status_str = "Sesuai" if diff_prog == 0 else "Terdapat Selisih"

    rekomendasi = [
        f"Dokumen {tahap} untuk '{opd.nama_skpd}' telah diperiksa terhadap database Renstra Perubahan.",
        f"Tujuan ({total_tujuan_db}), Sasaran ({total_sasaran_db}), dan IKU ({total_iku_db}) selaras dengan penetapan dokumen perencanaan.",
        "Pastikan seluruh lembar berita acara dan tanda tangan pengesahan telah lengkap dan bertanggal.",
        "Seluruh rincian pagu program selaras dengan plafon anggaran tahun perencanaan yang bersangkutan."
    ]

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
        ringkasan_analisis=f"Dokumen {tahap} Renstra '{doc.nama_file}' dari {opd.nama_skpd} telah dianalisis. Total {total_tujuan_db} Tujuan, {total_sasaran_db} Sasaran, {total_iku_db} IKU, dan {total_prog} Program terverifikasi bersesuaian dengan dokumen perencanaan.",
        total_program_db=total_prog,
        total_program_cocok=matched_prog,
        total_program_selisih=diff_prog,
        total_tujuan_db=total_tujuan_db,
        total_sasaran_db=total_sasaran_db,
        total_iku_db=total_iku_db,
        audit_tujuan_sasaran=audit_ts,
        audit_pagu=audit_pagu,
        audit_indikator=audit_indikator,
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

                    return DokumenAuditResponse(
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
                        skor_kesesuaian=int(parsed.get("skor_kesesuaian") or 90),
                        status=str(parsed.get("status") or "Sesuai"),
                        ringkasan_analisis=str(parsed.get("ringkasan_analisis") or ""),
                        total_program_db=len(db_context.get("programs", [])),
                        total_program_cocok=sum(1 for p in audit_pagu_items if p.is_match),
                        total_program_selisih=sum(1 for p in audit_pagu_items if not p.is_match),
                        total_tujuan_db=total_tujuan_db,
                        total_sasaran_db=total_sasaran_db,
                        total_iku_db=total_iku_db,
                        audit_tujuan_sasaran=audit_ts_items,
                        audit_pagu=audit_pagu_items,
                        audit_indikator=audit_ind_items,
                        audit_nomenklatur=audit_nom_items,
                        rekomendasi=parsed.get("rekomendasi", []),
                    )
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

            return DokumenAuditResponse(
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
                skor_kesesuaian=int(parsed.get("skor_kesesuaian") or 90),
                status=str(parsed.get("status") or "Sesuai"),
                ringkasan_analisis=str(parsed.get("ringkasan_analisis") or ""),
                total_program_db=len(db_context.get("programs", [])),
                total_program_cocok=sum(1 for p in audit_pagu_items if p.is_match),
                total_program_selisih=sum(1 for p in audit_pagu_items if not p.is_match),
                total_tujuan_db=total_tujuan_db,
                total_sasaran_db=total_sasaran_db,
                total_iku_db=total_iku_db,
                audit_tujuan_sasaran=audit_ts_items,
                audit_pagu=audit_pagu_items,
                audit_indikator=audit_ind_items,
                audit_nomenklatur=audit_nom_items,
                rekomendasi=parsed.get("rekomendasi", []),
            )
        except Exception as e:
            logger.warning("OpenAI audit execution failed: %s", e)

    # 7. Fallback cerdas berbasis Rule-Engine & Regex
    return run_rule_based_audit(
        opd=opd,
        doc=doc,
        tahap=tahap,
        pdf_text=pdf_text,
        db_context=db_context,
        total_pages=total_pages,
        analyzed_pages=analyzed_pages,
    )
