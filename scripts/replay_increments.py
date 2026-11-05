"""Replay the incremental loads until the source data is exhausted (demo scenario of DW_DESIGN section 12).

    python scripts/replay_increments.py            # monthly batches: simulate_increment + run_pipeline --mode incremental
Prerequisite: python -m etl.load_source --initial  and  python -m etl.run_pipeline --mode full.
Prints one markdown table row per batch: new source rows, staging/ODS/DW rows, run time, MQL / deals / sellers with a sale afterwards.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from sqlalchemy import text

from etl import config
from etl.db import get_engine
from etl.run_pipeline import run_pipeline
from etl.simulate_increment import WM, simulate


def last_source_date() -> pd.Timestamp:
    o = pd.read_csv(config.RAW_ECOMMERCE_DIR / "olist_orders_dataset.csv", usecols=["order_purchase_timestamp"])["order_purchase_timestamp"]
    d = pd.read_csv(config.RAW_MARKETING_DIR / "olist_closed_deals_dataset.csv", usecols=["won_date"])["won_date"]
    m = pd.read_csv(config.RAW_MARKETING_DIR / "olist_marketing_qualified_leads_dataset.csv", usecols=["first_contact_date"])["first_contact_date"]
    return max(pd.to_datetime(s).max() for s in (o, d, m))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--database", default=config.DB_NAME)
    parser.add_argument("--max-batches", type=int, default=24)
    args = parser.parse_args()
    engine = get_engine(args.database)
    stop = last_source_date()
    print(f"last record in the source files: {stop:%Y-%m-%d}")
    print("| Đợt | Nguồn đã đầy đủ đến | Bản ghi mới ở nguồn | Staging | ODS chèn / loại | DW chèn / cập nhật | Chạy pipeline (s) | Trong đó test (s) | MQL | Deal | Seller có đơn | Đơn | GMV |")
    print("| ---: | --- | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for i in range(1, args.max_batches + 1):
        with engine.connect() as c:
            row = c.execute(text("SELECT last_value::date FROM etl_log.watermark WHERE source_table = :w"), {"w": WM}).fetchone()
        prev = pd.Timestamp(row[0] if row else config.INITIAL_CUTOFF)
        if prev >= stop:
            break
        sim = simulate(args.database, None)
        res = run_pipeline("incremental", args.database, export=False)
        if res["fails"]:
            print("TESTS FAILED:", res["fails"][:3])
            sys.exit(1)
        with engine.connect() as c:
            r = c.execute(text("SELECT s.staging_rows, s.ods_inserted, s.ods_rejected, s.dw_inserted, s.dw_updated, s.duration_sec, s.test_sec, "
                               "m.mql, m.deals_won, m.sellers_with_sale, m.orders, m.gmv FROM etl_log.v_run_summary s JOIN etl_log.batch_metrics m USING (batch_id) "
                               "WHERE s.batch_id = :b"), {"b": res["batch"]}).one()
        print(f"| {i} | {sim['until']:%Y-%m-%d} | {sim['rows']:,} | {r[0]:,} | {r[1]:,} / {r[2]:,} | {r[3]:,} / {r[4]:,} | {r[5]} | {r[6]} | {r[7]:,} | {r[8]:,} | {r[9]:,} | {r[10]:,} | {float(r[11]):,.2f} |", flush=True)


if __name__ == "__main__":
    main()
