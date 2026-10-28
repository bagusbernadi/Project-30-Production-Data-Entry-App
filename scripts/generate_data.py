"""Project 30: data simulasi production_data (perakitan smartphone): Excel lama (kotor) vs data aplikasi (bersih + log). Seed tetap.

Dua kelompok data, masing-masing 75 hari kerja x 2 shift x 10 stasiun x 20 tray = 30.000 baris:
- Excel lama  (2026-03-02 s.d. 2026-06-12): diisi bebas, 2-3% baris kotor.
- Aplikasi    (2026-06-15 s.d. 2026-09-25): lewat form tervalidasi; plus ref_master, rejected_input, edit_log.
Hasil: data/sim/ (tidak di-commit) dan data/seed/ (kecil, di-commit: ref_master + 3 hari pertama data aplikasi).
Jalankan: python scripts/generate_data.py   (versi data: v1)
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SIM, SEED_DIR = ROOT / "data" / "sim", ROOT / "data" / "seed"
SEED = 30260302
DATA_VERSION = "v1"
N_DAYS, TRAYS, TRAY_CAP = 75, 20, 50
OLD_START, APP_START = "2026-03-02", "2026-06-15"
SHIFTS = ["Shift 1", "Shift 2"]
MODELS = ["Basic", "Plus", "Pro"]
MODEL_W = [0.40, 0.35, 0.25]
SUPPLIERS = ["Supplier A", "Supplier B", "Supplier C", "Supplier D"]
STATIONS = ["Solder Paste Printing", "Component Placement", "Reflow Soldering", "AOI Inspection",
            "Board Test (ICT)", "Screen Assembly", "Housing Assembly", "Final Inspection",
            "Functional Test", "Packaging"]
BASE_NG = [0.012, 0.011, 0.040, 0.008, 0.013, 0.010, 0.015, 0.012, 0.020, 0.003]
MODEL_FACTOR = {"Basic": 0.85, "Plus": 1.00, "Pro": 1.20}
OPERATORS = [f"OP{i:02d}" for i in range(1, 17)]
LOT_DAYS = 4                                   # satu lot supplier dipakai +-4 hari kerja
# Fakta tertanam (ground truth)
SUP_C_FUNCTIONAL = (2, 8, 2.0)                 # supplier C (indeks 2), Functional Test (indeks 8), pengali NG
PRO_PLACEMENT = (1, 1.8)                       # model Pro di Component Placement
BAD_LOT = dict(supplier=1, lot_index=6, stations=(2, 3), factor=3.0)   # lot Supplier B ke-7 (hari 24-27) naik NG di Reflow dan AOI
NEW_OP = dict(operator="OP16", station=4, shift="Shift 2", start_day=20, ramp_days=10, factor=2.5)
DIRTY_RATE = 0.025

rng = np.random.default_rng(SEED)


def slot_operator(s, sh_i, day):
    """Operator reguler per (stasiun, shift); OP16 menggantikan satu slot mulai hari NEW_OP['start_day']."""
    if (s == NEW_OP["station"] and SHIFTS[sh_i] == NEW_OP["shift"] and day >= NEW_OP["start_day"]):
        return NEW_OP["operator"], day - NEW_OP["start_day"]
    return OPERATORS[(s * 2 + sh_i) % 15], None


def lot_label(sup_i, day, start_ts):
    idx = (day + sup_i) // LOT_DAYS                      # lot bergeser per supplier
    first_day = max(0, idx * LOT_DAYS - sup_i)
    d0 = start_ts + pd.offsets.BDay(first_day)
    return f"B{d0.strftime('%y%m%d')}-{'ABCD'[sup_i]}{idx + 1:02d}", idx


def make_period(start, with_problem_lot=True):
    start_ts = pd.Timestamp(start)
    days = pd.bdate_range(start, periods=N_DAYS)
    rows = []
    for d, day in enumerate(days):
        lots = [lot_label(i, d, start_ts) for i in range(len(SUPPLIERS))]
        for sh_i, sh in enumerate(SHIFTS):
            noise = np.exp(rng.normal(0, 0.12, len(STATIONS)))
            for s, st in enumerate(STATIONS):
                op, since = slot_operator(s, sh_i, d)
                for tray in range(1, TRAYS + 1):
                    m = MODELS[int(rng.choice(3, p=MODEL_W))]
                    sup_i = int(rng.integers(0, len(SUPPLIERS)))
                    batch, lot_idx = lots[sup_i]
                    qty = TRAY_CAP if rng.random() > 0.10 else int(rng.integers(20, TRAY_CAP))
                    p = BASE_NG[s] * MODEL_FACTOR[m] * noise[s]
                    if sup_i == SUP_C_FUNCTIONAL[0] and s == SUP_C_FUNCTIONAL[1]:
                        p *= SUP_C_FUNCTIONAL[2]
                    if m == "Pro" and s == PRO_PLACEMENT[0]:
                        p *= PRO_PLACEMENT[1]
                    if with_problem_lot and sup_i == BAD_LOT["supplier"] and lot_idx == BAD_LOT["lot_index"] and s in BAD_LOT["stations"]:
                        p *= BAD_LOT["factor"]
                    if since is not None and since < NEW_OP["ramp_days"]:
                        p *= 1 + (NEW_OP["factor"] - 1) * (1 - since / NEW_OP["ramp_days"])
                    ng = int(rng.binomial(qty, min(p, 0.6)))
                    rows.append([day.date(), sh, st, m, batch, tray, SUPPLIERS[sup_i], op, qty - ng, ng])
    return pd.DataFrame(rows, columns=["entry_date", "shift", "station", "model", "batch_no", "tray_no",
                                       "supplier", "operator_id", "ok_qty", "ng_qty"])


# ---------- Excel lama (kotor) ----------
old = make_period(OLD_START)
old.insert(0, "row_no", np.arange(1, len(old) + 1))
n_dirty = int(round(len(old) * DIRTY_RATE))
pick = rng.permutation(len(old))[:n_dirty]
kinds = ["model_typo", "blank_cell", "qty_zero", "qty_over_cap", "duplicate_row", "unknown_supplier"]
dirty_log, dup_rows = [], []
for k, i in enumerate(pick):
    kind = kinds[k % len(kinds)]
    if kind == "model_typo":
        old.at[i, "model"] = {"Basic": "basic", "Plus": "Plus ", "Pro": "Prro"}[old.at[i, "model"]]
    elif kind == "blank_cell":
        old.at[i, ["station", "model", "supplier", "ok_qty", "ng_qty"][int(rng.integers(0, 5))]] = None
    elif kind == "qty_zero":
        old.at[i, "ok_qty"], old.at[i, "ng_qty"] = 0, 0
    elif kind == "qty_over_cap":
        old.at[i, "ok_qty"] = TRAY_CAP + int(rng.integers(5, 30))
    elif kind == "duplicate_row":
        dup_rows.append(i)
    else:
        old.at[i, "supplier"] = ["Supplier E", "Suplier C", "supplier a"][int(rng.integers(0, 3))]
    dirty_log.append([int(old.at[i, "row_no"]), kind])
old["_ord"] = np.arange(len(old), dtype=float)
dups = old.loc[dup_rows].copy()
dups["_ord"] += 0.5
old = pd.concat([old, dups]).sort_values("_ord").drop(columns="_ord").reset_index(drop=True)

# ---------- Data aplikasi (bersih) + tabel pendukung ----------
app = make_period(APP_START)
app.insert(0, "id", np.arange(1, len(app) + 1))
t = pd.to_datetime(app["entry_date"]) + pd.to_timedelta(np.where(app["shift"] == "Shift 1", 14, 22), unit="h") \
    + pd.to_timedelta(rng.integers(0, 3600, len(app)), unit="s")
app["created_at"] = t.dt.strftime("%Y-%m-%d %H:%M:%S")

edit_idx = sorted(int(i) for i in rng.choice(len(app), 90, replace=False))    # koreksi lewat fitur edit (ok/ng/supplier)
edits = []
for k, i in enumerate(edit_idx):
    col = ["ok_qty", "ng_qty", "supplier"][k % 3]
    old_v = app.at[i, col]
    if col == "supplier":
        new_v = SUPPLIERS[(SUPPLIERS.index(old_v) + 1) % len(SUPPLIERS)]
    else:
        delta = int(rng.integers(1, 4))
        new_v = max(0, int(old_v) - delta)
    edits.append([k + 1, int(app.at[i, "id"]), col, old_v, new_v, f"OP{int(rng.integers(1, 16)):02d}",
                  str(pd.Timestamp(app.at[i, "created_at"]) + pd.Timedelta(hours=int(rng.integers(1, 30))))])
    app.at[i, col] = new_v
edit_log = pd.DataFrame(edits, columns=["log_id", "record_id", "column_name", "old_value", "new_value", "edited_by", "edited_at"])

RULES = ["R_station_in_list", "R_qty_positive", "R_qty_within_cap", "R_no_duplicate", "R_batch_format", "R_date_not_future"]
rej = []
for k in range(int(len(app) * 0.015)):                 # +-1,5% isian ditolak validasi
    r = app.iloc[int(rng.integers(0, len(app)))]
    rule = RULES[int(rng.integers(0, len(RULES)))]
    snap = {"station": r["station"], "model": r["model"], "batch_no": r["batch_no"], "ok_qty": int(r["ok_qty"]), "ng_qty": int(r["ng_qty"])}
    if rule == "R_qty_within_cap":
        snap["ok_qty"] = TRAY_CAP + int(rng.integers(1, 20))
    elif rule == "R_qty_positive":
        snap["ok_qty"], snap["ng_qty"] = 0, 0
    elif rule == "R_batch_format":
        snap["batch_no"] = str(r["batch_no"]).replace("B", "").replace("-", "")
    rej.append([k + 1, f"{r['entry_date']} {int(rng.integers(6, 23)):02d}:{int(rng.integers(0, 60)):02d}:00", r["station"], rule, json.dumps(snap, ensure_ascii=False)])
rejected = pd.DataFrame(rej, columns=["reject_id", "submitted_at", "station", "rule_failed", "input_snapshot"])

ref = pd.DataFrame(
    [("station", v, True, "") for v in STATIONS] + [("model", v, True, "") for v in MODELS]
    + [("supplier", v, True, "") for v in SUPPLIERS] + [("operator", v, True, "") for v in OPERATORS]
    + [("tray", "default", True, TRAY_CAP)], columns=["list_type", "value", "active", "max_tray_qty"])

SIM.mkdir(parents=True, exist_ok=True)
SEED_DIR.mkdir(parents=True, exist_ok=True)
old.to_csv(SIM / "excel_lama.csv", index=False)
app.to_csv(SIM / "production_data.csv", index=False)
edit_log.to_csv(SIM / "edit_log.csv", index=False)
rejected.to_csv(SIM / "rejected_input.csv", index=False)
ref.to_csv(SIM / "ref_master.csv", index=False)
pd.DataFrame(dirty_log, columns=["row_no", "dirty_type"]).to_csv(SIM / "ground_truth_dirty.csv", index=False)
first_days = pd.bdate_range(APP_START, periods=3)
ref.to_csv(SEED_DIR / "ref_master.csv", index=False)
app[pd.to_datetime(app["entry_date"]).isin(first_days)].to_csv(SEED_DIR / "production_data_seed.csv", index=False)
gt = {"seed": SEED, "version": DATA_VERSION, "excel_lama": {"start": OLD_START, "rows": len(old), "dirty_rows": len(dirty_log)},
      "aplikasi": {"start": APP_START, "rows": len(app), "edits": len(edit_log), "rejected_inputs": len(rejected)},
      "facts": [
          {"id": 1, "fact": "Supplier C punya NG rate sekitar 2x lebih tinggi di Functional Test", "supplier": SUPPLIERS[2], "factor": SUP_C_FUNCTIONAL[2]},
          {"id": 2, "fact": "Model Pro yield lebih rendah di Component Placement", "factor": PRO_PLACEMENT[1]},
          {"id": 3, "fact": "Satu lot bermasalah +-4 hari menaikkan NG di Reflow Soldering dan AOI Inspection",
           "supplier": SUPPLIERS[BAD_LOT["supplier"]], "lot_index": BAD_LOT["lot_index"] + 1, "factor": BAD_LOT["factor"]},
          {"id": 4, "fact": "Operator baru lebih sering NG di 2 minggu pertama lalu membaik", **NEW_OP},
          {"id": 5, "fact": "Excel lama kotor", "dirty_rate": DIRTY_RATE, "types": kinds}]}
(SIM / "ground_truth.json").write_text(json.dumps(gt, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
print(f"excel_lama {len(old)} baris ({len(dirty_log)} kotor), production_data {len(app)} baris, edit {len(edit_log)}, "
      f"ditolak {len(rejected)}, seed {len(app[pd.to_datetime(app['entry_date']).isin(first_days)])} baris")
