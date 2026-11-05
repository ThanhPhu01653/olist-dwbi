"""Generate handoff/stats.md: CSV sizes + row/column/size counts of the source tables in each database.

    python scripts/report_stats.py                      # olist_dw and olist_full
    python scripts/report_stats.py --database olist_dw

Later phases extend this script with ODS / DW tables. All numbers come from the files and the databases.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from sqlalchemy import text

from etl import config
from etl.db import get_engine
from etl.load_source import SPECS, TABLE_NAMES


def fmt_bytes(n: int) -> str:
    return f"{n / 1024 / 1024:,.2f} MB" if n >= 1024 * 1024 else f"{n / 1024:,.1f} KB"


def csv_table() -> str:
    lines = ["| File | Thư mục | Dung lượng | Số dòng dữ liệu | Số cột |", "| --- | --- | ---: | ---: | ---: |"]
    tot_b = tot_r = 0
    for s in SPECS:
        df = pd.read_csv(s.path, dtype=str, keep_default_na=False)
        size = s.path.stat().st_size
        tot_b, tot_r = tot_b + size, tot_r + len(df)
        lines.append(f"| {s.path.name} | {s.path.parent.name} | {fmt_bytes(size)} | {len(df):,} | {len(df.columns)} |")
    lines.append(f"| **Tổng ({len(SPECS)} file)** | | **{fmt_bytes(tot_b)}** | **{tot_r:,}** | |")
    return "\n".join(lines)


def db_section(database: str) -> str:
    engine = get_engine(database)
    lines = [f"### Database `{database}`", "", "| Bảng | Số dòng | Số cột | Dung lượng (gồm index) |", "| --- | ---: | ---: | ---: |"]
    tot_rows = tot_cols = 0
    with engine.connect() as conn:
        for t in TABLE_NAMES:
            schema, name = t.split(".")
            n = conn.execute(text(f"SELECT count(*) FROM {t}")).scalar_one()
            c = conn.execute(text("SELECT count(*) FROM information_schema.columns WHERE table_schema=:s AND table_name=:t"),
                             {"s": schema, "t": name}).scalar_one()
            size = conn.execute(text("SELECT pg_total_relation_size(:t)"), {"t": t}).scalar_one()
            tot_rows, tot_cols = tot_rows + n, tot_cols + c
            lines.append(f"| {t} | {n:,} | {c} | {fmt_bytes(size)} |")
        db_size = conn.execute(text("SELECT pg_database_size(current_database())")).scalar_one()
        rej = conn.execute(text("SELECT count(*) FROM etl_log.rejected_rows")).scalar_one()
    lines.append(f"| **Tổng ({len(TABLE_NAMES)} bảng)** | **{tot_rows:,}** | **{tot_cols}** | |")
    lines += ["", f"- Dung lượng cả database: **{fmt_bytes(db_size)}**", f"- Số dòng trong etl_log.rejected_rows: **{rej:,}**"]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--database", action="append", help="database(s) to report (default: DB_NAME and DB_NAME_FULL)")
    args = parser.parse_args()
    parts = [f"# Thống kê dữ liệu (sinh tự động {datetime.now():%Y-%m-%d %H:%M})", "", "## File CSV nguồn", "", csv_table(), "",
             "## Bảng nguồn (oltp + crm)", ""]
    parts += [db_section(d) + "\n" for d in (args.database or [config.DB_NAME, config.DB_NAME_FULL])]
    out = config.ROOT / "handoff" / "stats.md"
    out.write_text("\n".join(parts), encoding="utf-8")
    print("\n".join(parts))
    print(f"Written {out.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
