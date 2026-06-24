# Single Exponential Smoothing (SES) Forecasting App

Aplikasi web full-stack untuk peramalan penjualan **Depot Jawara** menggunakan metode **Single Exponential Smoothing**. Backend FastAPI + SQLAlchemy, frontend Jinja2 + Tailwind CSS, autentikasi dual-mode (session cookie untuk web UI, JWT untuk API).

## Fitur

- **Overview** — dashboard ringkasan data (admin)
- **Products** — kelola daftar produk (admin)
- **Sales** — input & kelola data penjualan harian (admin)
- **Forecast** — kalkulator SES: pilih produk, alpha, rentang tanggal → hasil forecast + MAPE + langkah perhitungan (admin)
- **Forecasts** — riwayat semua forecast yang pernah dibuat (admin & owner)
- **Chart** — visualisasi aktual vs forecast (admin & owner)

Detail lengkap tiap fitur, rumus SES, dan flow website ada di [DOCS.md](DOCS.md).

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy
- **Frontend:** Jinja2 templates, Tailwind CSS, DataTables (jQuery)
- **Database:** SQLite (default) atau MySQL
- **Auth:** Session cookie (web UI) + JWT (API)

## Menjalankan secara lokal

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Buka `http://localhost:8000`. Akun default (auto-dibuat saat pertama jalan):

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | Admin |
| `owner` | `owner123` | Owner |

## Testing

```bash
pytest
pytest --cov=. --cov-report=html
```

## Konfigurasi

Buat file `.env` (opsional, default pakai SQLite):

```bash
DATABASE_URL=mysql+pymysql://user:pass@host:3306/sales_app  # omit untuk SQLite
SECRET_KEY=random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Deploy dengan Docker

```bash
docker-compose up -d
```

## Migrasi SQLite → MySQL

```bash
python migrate_to_mysql.py
```

## Dokumentasi

- [DOCS.md](DOCS.md) — dokumentasi fitur, rumus SES, dan flow website
- [CLAUDE.md](CLAUDE.md) — panduan arsitektur & development untuk kontributor
