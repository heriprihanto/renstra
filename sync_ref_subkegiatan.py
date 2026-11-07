#!/usr/bin/env python3
"""
Script to fetch all subkegiatan records from SIPD-RI Pemutakhiran AJAX endpoint
and store them into PostgreSQL table `ref_subkegiatan`.
"""

import os
import re
import sys
import json
import time
import urllib.parse
import httpx
import psycopg

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CURL_FILE = os.path.join(CURRENT_DIR, "curlsubkeg.sh")
ENV_FILE = os.path.join(CURRENT_DIR, "Backend", ".env")
OUTPUT_JSON = "/home/herry/subkeg_all.json"


def load_env(env_path):
    config = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    config[key.strip()] = val.strip().strip("'\"")
    return config


def parse_curl_command(curl_path):
    with open(curl_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract URL
    url_match = re.search(r"--url '([^']+)'", content) or re.search(r"curl\s+'([^']+)'", content)
    url = url_match.group(1) if url_match else "https://sipd-ri.kemendagri.go.id/pemutakhiran/7a109b4bda9d06698f73a4966a4816a9f1ff6228/?m=bukadata"

    # Extract headers
    headers = {}
    for h in re.findall(r"-H '([^:]+):\s*([^']+)'", content):
        headers[h[0].strip()] = h[1].strip()

    # Extract cookies
    cookie_str = ""
    cookie_match = re.search(r"-b '([^']+)'", content)
    if cookie_match:
        cookie_str = cookie_match.group(1)

    cookies = {}
    if cookie_str:
        for item in cookie_str.split(";"):
            item = item.strip()
            if "=" in item:
                k, v = item.split("=", 1)
                cookies[k.strip()] = urllib.parse.unquote(v.strip())

    # Extract data-raw
    data_match = re.search(r"--data-raw '([^']+)'", content)
    raw_data = data_match.group(1) if data_match else ""
    data_dict = dict(urllib.parse.parse_qsl(raw_data))

    return url, headers, cookies, data_dict


def main():
    print("=" * 60)
    print("PENARIKAN DATA MASTER SUBKEGIATAN SIPD-RI KE ref_subkegiatan")
    print("=" * 60)

    # 1. Parse curl command
    url, headers, cookies, base_data = parse_curl_command(CURL_FILE)
    print(f"Target URL : {url}")
    print(f"Versi Data : {base_data.get('versipemutakhiran', '20271')}")

    # 2. Database connection config
    db_cfg = load_env(ENV_FILE)
    db_host = db_cfg.get("POSTGRES_SERVER", "192.168.50.75")
    db_name = db_cfg.get("POSTGRES_DB", "db_renstra")
    db_user = db_cfg.get("POSTGRES_USER", "monevrkpd")
    db_pass = db_cfg.get("POSTGRES_PASSWORD", "heriprihanto140286")
    db_port = db_cfg.get("POSTGRES_PORT", "5432")

    print(f"Database   : {db_user}@{db_host}:{db_port}/{db_name}")

    # Test DB Connection
    try:
        conn = psycopg.connect(
            host=db_host,
            dbname=db_name,
            user=db_user,
            password=db_pass,
            port=db_port,
            autocommit=True
        )
        print("Koneksi Database PostgreSQL BERHASIL!")
    except Exception as e:
        print(f"GAGAL terhubung ke Database: {e}")
        sys.exit(1)

    # 3. Fetch data in pages
    start = 0
    step = 500  # SIPD-RI max supported page length is 500
    all_data = []
    total_records = None
    page_num = 1

    print("\nMemulai penarikan data...")

    client = httpx.Client(headers=headers, cookies=cookies, timeout=60.0)

    while True:
        req_data = dict(base_data)
        req_data["start"] = str(start)
        req_data["length"] = str(step)
        req_data["draw"] = str(page_num)

        retries = 3
        batch = None
        while retries > 0:
            try:
                t0 = time.time()
                resp = client.post(url, data=req_data)
                dur = time.time() - t0
                if resp.status_code == 200:
                    res_json = resp.json()
                    if total_records is None:
                        total_records = res_json.get("recordsTotal", 0)
                        print(f"Total data di SIPD-RI: {total_records} baris.")

                    batch = res_json.get("data", [])
                    print(f"  [Halaman {page_num:02d}] start={start:5d} -> Didapat {len(batch):3d} baris ({dur:.2f}s). Total terambil: {len(all_data) + len(batch)}/{total_records}")
                    break
                else:
                    print(f"  [Error {resp.status_code}] Percobaan ulang...")
                    retries -= 1
                    time.sleep(2)
            except Exception as ex:
                print(f"  [Exception] {ex}, mencoba ulang ({retries} sisa)...")
                retries -= 1
                time.sleep(3)

        if batch is None or len(batch) == 0:
            print("  Tidak ada data tambahan, penarikan selesai.")
            break

        all_data.extend(batch)
        if total_records and len(all_data) >= total_records:
            print(f"Seluruh data ({len(all_data)} baris) berhasil ditarik lengkap!")
            break

        start += step
        page_num += 1
        time.sleep(0.5)

    client.close()

    print(f"\nTotal data berhasil diunduh: {len(all_data)} baris.")

    # 4. Save JSON backup
    try:
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump({"total": len(all_data), "data": all_data}, f, ensure_ascii=False, indent=2)
        print(f"Backup file JSON berhasil disimpan di: {OUTPUT_JSON}")
    except Exception as e:
        print(f"Peringatan: Gagal menyimpan backup JSON: {e}")

    # 5. Insert into Database table `ref_subkegiatan`
    print("\nMenyimpan data ke tabel `ref_subkegiatan`...")

    insert_sql = """
    INSERT INTO ref_subkegiatan (
        tahun, versipemutakhiran, idpemutakhiran, jnspemda,
        kodebidang, uraibidang, kodeprogram, uraiprogram,
        kodekegiatan, uraikegiatan, kodesubkegiatan, uraisubkegiatan,
        referensi_kodesubkegiatan, referensi_uraisubkegiatan, referensi_subkegiatan,
        definisi_operasional, bidang_pelaksana, spm, jenis,
        bidang, program, kegiatan, subkegiatan, subkegiatan_tampil,
        kinerja, indikator, status_indikator, satuan, disabled,
        tag, pemda, ketergunaan, no
    ) VALUES (
        %(tahun)s, %(versipemutakhiran)s, %(idpemutakhiran)s, %(jnspemda)s,
        %(kodebidang)s, %(uraibidang)s, %(kodeprogram)s, %(uraiprogram)s,
        %(kodekegiatan)s, %(uraikegiatan)s, %(kodesubkegiatan)s, %(uraisubkegiatan)s,
        %(referensi_kodesubkegiatan)s, %(referensi_uraisubkegiatan)s, %(referensi_subkegiatan)s,
        %(definisi_operasional)s, %(bidang_pelaksana)s, %(spm)s, %(jenis)s,
        %(bidang)s, %(program)s, %(kegiatan)s, %(subkegiatan)s, %(subkegiatan_tampil)s,
        %(kinerja)s, %(indikator)s, %(status_indikator)s, %(satuan)s, %(disabled)s,
        %(tag)s, %(pemda)s, %(ketergunaan)s, %(no)s
    );
    """

    with conn.cursor() as cur:
        # Truncate existing table before fresh sync
        print("  Mengosongkan tabel `ref_subkegiatan` sebelum sinkronisasi baru...")
        cur.execute("TRUNCATE TABLE ref_subkegiatan RESTART IDENTITY;")

        records_to_insert = []
        for row in all_data:
            rec = {
                "tahun": str(row.get("tahun") or ""),
                "versipemutakhiran": str(row.get("versipemutakhiran") or ""),
                "idpemutakhiran": str(row.get("idpemutakhiran") or ""),
                "jnspemda": str(row.get("jnspemda") or ""),
                "kodebidang": str(row.get("kodebidang") or ""),
                "uraibidang": str(row.get("uraibidang") or ""),
                "kodeprogram": str(row.get("kodeprogram") or ""),
                "uraiprogram": str(row.get("uraiprogram") or ""),
                "kodekegiatan": str(row.get("kodekegiatan") or ""),
                "uraikegiatan": str(row.get("uraikegiatan") or ""),
                "kodesubkegiatan": str(row.get("kodesubkegiatan") or ""),
                "uraisubkegiatan": str(row.get("uraisubkegiatan") or ""),
                "referensi_kodesubkegiatan": row.get("referensi_kodesubkegiatan"),
                "referensi_uraisubkegiatan": row.get("referensi_uraisubkegiatan"),
                "referensi_subkegiatan": str(row.get("referensi_subkegiatan") or ""),
                "definisi_operasional": row.get("definisi_operasional"),
                "bidang_pelaksana": row.get("bidang_pelaksana"),
                "spm": str(row.get("spm") or ""),
                "jenis": str(row.get("jenis") or ""),
                "bidang": str(row.get("bidang") or ""),
                "program": str(row.get("program") or ""),
                "kegiatan": str(row.get("kegiatan") or ""),
                "subkegiatan": str(row.get("subkegiatan") or ""),
                "subkegiatan_tampil": str(row.get("subkegiatan_tampil") or ""),
                "kinerja": str(row.get("kinerja") or ""),
                "indikator": str(row.get("indikator") or ""),
                "status_indikator": row.get("status_indikator"),
                "satuan": str(row.get("satuan") or ""),
                "disabled": str(row.get("disabled") or "0"),
                "tag": str(row.get("tag") or ""),
                "pemda": str(row.get("pemda") or "") if row.get("pemda") is not None else None,
                "ketergunaan": str(row.get("ketergunaan") or ""),
                "no": int(row.get("no")) if row.get("no") is not None and str(row.get("no")).isdigit() else None,
            }
            records_to_insert.append(rec)

        print(f"  Menyisipkan {len(records_to_insert)} baris ke tabel ref_subkegiatan...")
        cur.executemany(insert_sql, records_to_insert)

        # Check count
        cur.execute("SELECT COUNT(*) FROM ref_subkegiatan;")
        total_in_db = cur.fetchone()[0]
        print(f"BERHASIL! Total baris di tabel `ref_subkegiatan`: {total_in_db} baris.")

    conn.close()
    print("\nSinkronisasi selesai dengan sukses.")


if __name__ == "__main__":
    main()
