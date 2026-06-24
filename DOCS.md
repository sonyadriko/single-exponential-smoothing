# Dokumentasi Fitur — Depot Jawara Forecasting App

## Akses & Role

| Role | Akses |
|------|-------|
| **Admin** | Semua fitur: input data, kelola produk, buat forecast |
| **Owner** | Read-only: lihat Forecasts dan Chart |

Login default:
- Admin: `admin` / `admin123`
- Owner: `owner` / `owner123`

---

## 1. Dashboard `/dashboard`
**Hanya admin.**

Dashboard ringkasan kondisi data:
- Total produk, total data penjualan, total forecast yang pernah dibuat
- Tabel 10 penjualan terbaru

---

## 2. Products `/products`
**Hanya admin.**

Manajemen daftar produk yang tersedia di sistem.

**Aksi:**
- Tambah produk baru (nama)
- Hapus produk

> Produk yang dihapus tidak otomatis menghapus data penjualan terkait.

---

## 3. Sales `/sales`
**Hanya admin.**

Input dan kelola data penjualan harian per produk.

Tabel menggunakan DataTables — fitur bawaan: sorting per kolom, pagination, search box global.

**Filter bar:**
| Filter | Keterangan |
|--------|-----------|
| Product | Dropdown pilih produk tertentu atau semua produk |
| From / To | Filter rentang tanggal |

Filter dikirim ke backend (server-side), bukan disaring di browser.

**Aksi:**
- **Add Sale** — form modal: tanggal (default hari ini), pilih produk, qty
- **Delete** — konfirmasi modal sebelum hapus

---

## 4. Forecast `/forecast`
**Hanya admin.**

Kalkulator Single Exponential Smoothing (SES) untuk menghasilkan prediksi penjualan periode berikutnya.

**Parameter input:**

| Parameter | Keterangan |
|-----------|-----------|
| Alpha (α) | Koefisien smoothing, nilai 0–1. Makin tinggi = makin responsif ke data terbaru |
| Product | Pilih satu produk atau semua produk sekaligus |
| Start Date / End Date | Rentang data penjualan yang dipakai kalkulasi |
| Next Period Date | Tanggal yang ingin diprediksi |

**Formula SES:**
```
F(t+1) = α × A(t) + (1-α) × F(t)
```
- `F(t+1)` = forecast periode berikutnya
- `A(t)` = nilai aktual periode ini
- `F(t)` = forecast periode ini
- Inisialisasi: `F1 = A1`

**Output setelah kalkulasi:**
- Nilai forecast periode berikutnya
- Tanggal yang diprediksi
- Nilai alpha yang dipakai
- MAPE (Mean Absolute Percentage Error) — akurasi model, semakin kecil semakin baik
- Chart perbandingan garis aktual vs forecast
- Tabel langkah perhitungan per periode

Hasil forecast otomatis tersimpan ke database saat kalkulasi selesai.

---

## 5. Forecasts `/forecasts`
**Admin & Owner.**

Riwayat semua forecast yang pernah dibuat, diurutkan dari terbaru.

Kolom: tanggal dibuat, produk, alpha, nilai forecast, tanggal prediksi, MAPE.

---

## 6. Chart `/chart`
**Admin & Owner.**

Visualisasi grafis — membandingkan data aktual penjualan dengan hasil forecast per produk dalam satu grafik.

---

## Flow Website

### Routing & Redirect (`main.py`)

```
GET /            → sudah login? redirect ke /dashboard (admin) atau /forecasts (owner)
                   belum login? redirect ke /login
GET /login       → sudah login? redirect sesuai role (lihat atas)
                   belum login? tampilkan form login
POST /login      → verifikasi username/password → buat session → redirect sesuai role
GET /logout      → hapus session → redirect ke /login
GET /admin       → redirect 301 ke /dashboard (alias lama)
GET /owner       → redirect 301 ke /forecasts (alias lama)
```

Tiap halaman fitur (`/dashboard`, `/products`, `/sales`, `/forecast`, `/forecasts`, `/chart`) melakukan 2 pengecekan berurutan sebelum render:
1. `is_authenticated(request)` — belum login → redirect ke `/login`
2. Untuk halaman admin-only (`/dashboard`, `/products`, `/sales`, `/forecast`) — kalau bukan admin → redirect ke `/forecasts`

`/forecasts` dan `/chart` bisa diakses admin maupun owner.

### Alur Request (per layer)

```
Browser (template / static/js/api.js)
   │  fetch() dengan session cookie / Bearer token
   ▼
api/*.py (FastAPI router)         ← validasi request via schemas/*.py (Pydantic)
   │
   ▼
services/*.py                    ← business logic (mis. calculate_ses_with_steps)
   │
   ▼
repositories/*.py                 ← query SQLAlchemy ke DB
   │
   ▼
models.py (ORM) ──> database.py (engine: SQLite/MySQL)
```

Web UI (Jinja2 template di `main.py`) dan REST API (`api/`) sama-sama lewat layer service/repository yang sama — bedanya hanya cara autentikasi (session cookie vs JWT Bearer).

### Alur fitur Forecast (paling kompleks)

1. User isi form di `/forecast`: pilih produk, alpha, rentang tanggal, tanggal target prediksi
2. Frontend (`api.js`) → `POST /api/forecast`
3. `api/forecast.py` ambil data `Sales` sesuai filter via repository, urutkan ascending by date
4. `services/forecast_service.py::calculate_ses_with_steps()` jalankan rekursi SES, hasilkan `forecasts`, `steps`, `mape`
5. Hasil + next period forecast disimpan ke tabel `Forecasts`
6. Response dikirim balik ke frontend → render chart (aktual vs forecast) + tabel langkah perhitungan

---

## Catatan Teknis

- **MAPE** dihitung sebagai rata-rata `|Aktual - Forecast| / Aktual × 100%` per periode
- Data diurutkan ascending berdasarkan tanggal sebelum kalkulasi
- Forecast pertama `F1` disamakan dengan nilai aktual pertama `A1`
- Implementasi SES: `services/forecast_service.py` → `calculate_ses_with_steps()`
