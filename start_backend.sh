#!/usr/bin/env bash

# Pindah ke direktori Backend
cd "$(dirname "$0")/Backend" || exit 1

# Cek apakah virtual environment ada
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Peringatan: .venv tidak ditemukan di folder Backend. Menggunakan python global..."
fi

# Jalankan server FastAPI dengan Uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

