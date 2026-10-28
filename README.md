[← Back to portfolio](https://bagusbernadi.github.io/)

# Project 30: Production Data Entry App + Dashboard

**Status: Design (rancangan).**

**Tujuan:** Membangun aplikasi input data produksi yang tervalidasi untuk menggantikan pencatatan Excel manual, yang langsung menampilkan yield dan NG rate per stasiun, model, dan supplier, sehingga masalah kualitas terlihat di hari yang sama dan waktu rekap manual bisa dihemat.

Halaman rancangan: https://bagusbernadi.github.io/Project-30-Production-Data-Entry-App/

| | |
|---|---|
| Kategori | Manufaktur (perakitan smartphone) |
| Tingkat | Sulit |
| Data | Data simulasi meniru struktur tabel production_data (data seed disertakan) |
| Tools | Python (Streamlit, pandas, SQLAlchemy, pytest), SQLite + PostgreSQL (Neon), Plotly, GitHub Actions, gitleaks, Docker (opsional) |

## 1. Problem
Bagaimana mengganti pencatatan Excel manual menjadi aplikasi input yang tervalidasi, yang langsung menghasilkan dashboard yield/NG dan insight per stasiun, model, dan supplier?

## 2. Data
- Data simulasi buatan sendiri, dibuat oleh `scripts/generate_data.py` (Versi: v1; Tanggal dibuat: 28 Okt 2026; Seed: 30260302).
- 10 stasiun perakitan smartphone, 3 model (Basic, Plus, Pro), 4 supplier anonim, 2 shift, ±3 bulan. Hasil v1: 30.125 baris data Excel lama (750 baris kotor, 2,5%) dan 30.000 baris data aplikasi, dengan tabel `ref_master`, `edit_log` (90 koreksi), dan `rejected_input` (450 isian ditolak). Data seed kecil (1.200 baris, 3 hari pertama aplikasi) ada di `data/seed/` dan di-commit; data lengkap dibuat ulang oleh generator (`data/sim/`, tidak di-commit).
- Tidak memakai data perusahaan.

## 3. Analysis
Belum dikerjakan. Rencana langkah ada di bagian Work Plan pada halaman rancangan.

## 4. Recommendation
Belum dikerjakan.

## 5. Impact
Belum dikerjakan. Angka dampak nanti diberi label `estimated` / `simulated`.

## Batasan yang sudah diketahui
- Data simulasi: angka hasil membuktikan aplikasi dan metode bekerja, bukan kondisi pabrik sebenarnya.
- Kredensial yang pernah ter-push di repo lama dianggap bocor dan wajib diganti.
- Validasi tidak menangkap angka keliru yang masih masuk akal.
- Angka jam dihemat dan error turun adalah estimasi (label simulated/estimated).

## Struktur repository
```
index.html          # halaman rancangan (GitHub Pages)
README.md
app/                # (rencana) form input, dashboard, validasi, modul database
sql/                # (rencana) skema dan view KPI
scripts/            # (rencana) generator data simulasi
tests/              # (rencana) unit test
docs/               # (rencana) audit, aturan validasi, kamus data
```
