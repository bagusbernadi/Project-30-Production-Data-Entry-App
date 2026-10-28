# Data

Semua data di project ini simulasi (karangan), dibuat oleh `scripts/generate_data.py` dengan seed tetap. Tidak ada dataset publik atau data perusahaan, jadi tidak ada masalah lisensi.

| | |
|---|---|
| Versi data | v1 |
| Tanggal dibuat | 28 Okt 2026 |
| Seed | 30260302 |
| Cara membuat ulang | `python3 scripts/generate_data.py` (dari folder project) |
| Hasil v1 | Excel lama 30.125 baris (750 kotor), aplikasi 30.000 baris, `edit_log` 90, `rejected_input` 450 |

- `seed/` (di-commit): `ref_master.csv` dan `production_data_seed.csv` (1.200 baris, 3 hari pertama data aplikasi).
- `sim/` (tidak di-commit): `excel_lama.csv`, `production_data.csv`, `ref_master.csv`, `edit_log.csv`, `rejected_input.csv`, `ground_truth_dirty.csv`, `ground_truth.json`.

Jejak pembuatan (seed, commit, SHA-256 hasil) dicatat di repo `DataCenter`, folder `simulasi/`. Jika generator, seed, atau versi library berubah, hasil berubah dan versi data harus dinaikkan.
