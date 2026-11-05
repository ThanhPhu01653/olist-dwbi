"""Build the whole project from scratch with ONE command:   python scripts/rebuild_all.py [--drop] [--skip-full-db]

    [drop both databases] -> setup_db -> load_source --initial (olist_dw) -> load_source --full (olist_full, for EDA)
    -> run_pipeline --mode full -> replay_increments (11 monthly batches: simulate_increment + incremental) -> run_pipeline --mode incremental (tests + export)
Prerequisites: PostgreSQL running, .env filled in, the Kaggle CSV files in data/raw/ (see README.md). Takes about 7 minutes.
--drop             first DROP olist_dw and olist_full (a true "from zero" run; all data is rebuilt from the CSV files)
--skip-full-db     do not load olist_full (only needed for EDA and the benchmark of the source schema is NOT affected)
--signature FILE   before dropping, save a content signature of every dimension / fact (row count, sum of money, checksum on natural keys)
--compare FILE     after the rebuild, compare with a saved signature
Writes handoff/rebuild-report.md (steps, seconds, test result, comparison). Only a one-line summary of every step is printed.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sqlalchemy import text

from etl import config
from etl.db import get_engine


def load_compare():
    spec = importlib.util.spec_from_file_location("compare_databases", ROOT / "scripts" / "compare_databases.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def signature(database: str) -> dict:
    cmp = load_compare()
    with get_engine(database).connect() as conn:
        return {t: list(cmp.measure(conn, t)) for t in cmp.CHECKS}


def drop_databases() -> None:
    eng = get_engine("postgres", isolation_level="AUTOCOMMIT")
    with eng.connect() as c:
        for name in (config.DB_NAME, config.DB_NAME_FULL):
            c.execute(text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))


def run(cmd: list[str]) -> tuple[int, str, float]:
    t0 = time.perf_counter()
    p = subprocess.run([sys.executable, *cmd], capture_output=True, text=True, cwd=ROOT)
    out = (p.stdout + p.stderr).strip().splitlines()
    last = out[-1] if out else ""
    if cmd[0].endswith("replay_increments.py"):
        batches = [l for l in out if re.match(r"\| \d+ \|", l)]
        last = f"{len(batches)} đợt hằng tháng; sau đợt cuối: " + (batches[-1].strip("| ") if batches else "?")
    elif last.startswith("pipeline "):
        m = re.search(r"tests \{[^}]*\}", last)
        last = (m.group(0) if m else "") + "; " + (re.search(r"total [\d.]+s", last).group(0) if re.search(r"total [\d.]+s", last) else "")
    return p.returncode, last, time.perf_counter() - t0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--drop", action="store_true")
    ap.add_argument("--skip-full-db", action="store_true")
    ap.add_argument("--signature")
    ap.add_argument("--compare")
    a = ap.parse_args()
    t_all = time.perf_counter()
    started = datetime.now()
    rows: list[tuple[str, float, str]] = []

    if a.signature:
        Path(a.signature).write_text(json.dumps(signature(config.DB_NAME)), encoding="utf-8")
        print(f"signature of {config.DB_NAME} saved to {a.signature}")
    if a.drop:
        t0 = time.perf_counter()
        drop_databases()
        rows.append(("drop olist_dw + olist_full", time.perf_counter() - t0, "dropped"))
        print(f"[{rows[-1][1]:6.1f}s] {rows[-1][0]}: {rows[-1][2]}")

    steps = [("setup_db (schemas, DDL, procedures, views)", ["-m", "etl.setup_db"]),
             ("load_source --initial (olist_dw, to 2017-12-31)", ["-m", "etl.load_source", "--initial"])]
    if not a.skip_full_db:
        steps.append(("load_source --full (olist_full)", ["-m", "etl.load_source", "--full", "--database", config.DB_NAME_FULL]))
    steps += [("run_pipeline --mode full (initial state)", ["-m", "etl.run_pipeline", "--mode", "full", "--no-export"]),
              ("replay_increments (11 x simulate + incremental)", ["scripts/replay_increments.py"]),
              ("run_pipeline --mode incremental (tests + export_powerbi)", ["-m", "etl.run_pipeline", "--mode", "incremental"])]
    ok = True
    final_line = ""
    for name, cmd in steps:
        rc, last, secs = run(cmd)
        rows.append((name, secs, last[:230] if rc == 0 else f"FAILED (exit {rc}): {last[:200]}"))
        print(f"[{secs:6.1f}s] {name}: {'ok' if rc == 0 else 'FAILED'}")
        if rc != 0:
            ok = False
            print("   " + last[:300])
            break
        final_line = last
    cmp_note = "không so sánh (không có --compare)"
    if ok and a.compare:
        before = json.loads(Path(a.compare).read_text(encoding="utf-8"))
        after = signature(config.DB_NAME)
        diff = [t for t in before if before[t] != after[t]]
        cmp_note = f"{len(before) - len(diff)}/{len(before)} bảng dim/fact khớp tín hiệu trước khi xoá (số dòng, tổng tiền, checksum nội dung)" + (f"; LỆCH: {diff}" if diff else "")
        print("compare:", cmp_note)
    total = time.perf_counter() - t_all
    md = [f"# Kiểm chứng tái lập – chạy lại từ đầu bằng `python scripts/rebuild_all.py{' --drop' if a.drop else ''}` ({started:%Y-%m-%d %H:%M})", "",
          "| Bước | Thời gian (giây) | Kết quả (dòng cuối) |", "| --- | ---: | --- |"]
    md += [f"| {n} | {s:.1f} | {r.replace('|', '/')} |" for n, s, r in rows]
    md += ["", f"**Tổng thời gian: {total:.0f} giây ({total / 60:.1f} phút).** Kết quả: {'THÀNH CÔNG' if ok else 'THẤT BẠI'}.", "", f"So sánh với trạng thái trước khi xoá: {cmp_note}.", ""]
    (ROOT / "handoff" / "rebuild-report.md").write_text("\n".join(md), encoding="utf-8")
    print(f"total {total:.0f}s ({total / 60:.1f} min); {'OK' if ok else 'FAILED'}; report: handoff/rebuild-report.md")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
