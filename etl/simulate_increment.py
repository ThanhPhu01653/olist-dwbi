"""Simulate the source systems receiving new data:  python -m etl.simulate_increment [--until YYYY-MM-DD]

The Kaggle files are static, so after the initial load (everything up to 2017-12-31, DW_DESIGN section 12) this script
"replays" the next period into oltp / crm: every record that is not yet in the source and whose timestamp is <= --until.
Default --until = end of the month after the last simulated date (watermark 'source.simulated_until' in etl_log.watermark,
2017-12-31 right after the initial load).

  orders by order_purchase_timestamp + their customers (customer_id is generated per order), items, payments, reviews;
  mql by first_contact_date; closed_deals by won_date.
A deal needs its MQL (foreign key of the CRM): if the MQL has a later first_contact_date (a deal registered before the contact
date, e.g. mql b91cf881...) the MQL is loaded together with the deal. Re-running the same --until inserts nothing.
Limitation: orders arrive with their final status from the CSV (intermediate statuses cannot be simulated).
"""
from __future__ import annotations

import argparse
import sys
import time

import pandas as pd

from . import config
from .db import get_engine
from .load_source import ECOM, MKT, check_files, copy_df, db_columns
from .log import job_run, new_batch_id

WM = "source.simulated_until"


def _existing(cur, table: str, cols: list[str]) -> set:
    cur.execute(f"SELECT {', '.join(cols)} FROM {table}")
    rows = cur.fetchall()
    return {r[0] if len(cols) == 1 else tuple(r) for r in rows}


def _insert(cur, engine, batch: int, table: str, df: pd.DataFrame, pk: list[str], parent_checks: list[tuple[str, set, str]], results: list) -> pd.DataFrame:
    """Validate df (NOT NULL, duplicate key, foreign keys) and insert it; rejected rows go to etl_log.rejected_rows."""
    t0 = time.perf_counter()
    cols, required = db_columns(cur, table)
    with job_run(engine, batch, f"simulate_increment.{table}", "source", table) as run:
        run.rows_read = len(df)
        df = df[cols]
        bad = pd.Series(False, index=df.index)
        for c in required:
            m = df[c] == ""
            if m.any():
                run.log_rejected(table, f"NOT NULL column {c} is empty", df[m])
                bad |= m
        df = df[~bad]
        dup = df.duplicated(pk, keep="first")
        if dup.any():
            run.log_rejected(table, f"duplicate primary key ({', '.join(pk)})", df[dup])
            df = df[~dup]
        for col, parents, parent_name in parent_checks:
            orphan = ~df[col].isin(parents)
            if orphan.any():
                run.log_rejected(table, f"orphan: {col} not found in {parent_name}", df[orphan])
                df = df[~orphan]
        cur.execute(f"CREATE TEMP TABLE tmp_sim (LIKE {table}) ON COMMIT DROP")
        copy_df(cur, "tmp_sim", df, cols)
        cur.execute(f"INSERT INTO {table} ({', '.join(cols)}) SELECT {', '.join(cols)} FROM tmp_sim ON CONFLICT DO NOTHING")
        run.rows_inserted = cur.rowcount
        cur.execute("DROP TABLE tmp_sim")
        results.append({"table": table, "rows": run.rows_inserted, "rejected": run.rows_rejected, "seconds": round(time.perf_counter() - t0, 1)})
    return df


def simulate(database: str, until: str | None) -> dict:
    check_files()
    engine = get_engine(database)
    raw = engine.raw_connection()
    results: list[dict] = []
    try:
        cur = raw.cursor()
        cur.execute("SELECT last_value::date FROM etl_log.watermark WHERE source_table = %s", (WM,))
        row = cur.fetchone()
        prev = pd.Timestamp(row[0] if row else config.INITIAL_CUTOFF)
        until_ts = pd.Timestamp(until) if until else prev + pd.offsets.MonthEnd(1)
        if until_ts <= prev:
            print(f"Nothing to do: source already simulated up to {prev:%Y-%m-%d} (requested {until_ts:%Y-%m-%d}).")
            return {"until": prev, "rows": 0, "skipped": True}
        end = until_ts + pd.Timedelta(days=1)       # exclusive bound
        batch = new_batch_id(engine)
        t0 = time.perf_counter()

        rd = lambda path: pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")
        have = {t: _existing(cur, t, pk) for t, pk in [("oltp.orders", ["order_id"]), ("oltp.customers", ["customer_id"]), ("crm.mql", ["mql_id"]),
                                                      ("oltp.products", ["product_id"]), ("oltp.sellers", ["seller_id"])]}
        orders = rd(ECOM / "olist_orders_dataset.csv")
        ts = pd.to_datetime(orders["order_purchase_timestamp"], errors="coerce")
        new_orders = orders[(ts < end) & ~orders["order_id"].isin(have["oltp.orders"]) & ts.notna()]
        ids = set(new_orders["order_id"])

        cust = rd(ECOM / "olist_customers_dataset.csv")
        cust_new = cust[cust["customer_id"].isin(set(new_orders["customer_id"])) & ~cust["customer_id"].isin(have["oltp.customers"])]
        _insert(cur, engine, batch, "oltp.customers", cust_new, ["customer_id"], [], results)
        customers_present = have["oltp.customers"] | set(cust_new["customer_id"])
        orders_ok = _insert(cur, engine, batch, "oltp.orders", new_orders, ["order_id"], [("customer_id", customers_present, "oltp.customers")], results)
        orders_present = have["oltp.orders"] | set(orders_ok["order_id"])
        for table, fname, pk, extra in [
            ("oltp.order_items", "olist_order_items_dataset.csv", ["order_id", "order_item_id"],
             [("product_id", have["oltp.products"], "oltp.products"), ("seller_id", have["oltp.sellers"], "oltp.sellers")]),
            ("oltp.order_payments", "olist_order_payments_dataset.csv", ["order_id", "payment_sequential"], []),
            ("oltp.order_reviews", "olist_order_reviews_dataset.csv", ["review_id", "order_id"], []),
        ]:
            d = rd(ECOM / fname)
            d = d[d["order_id"].isin(ids)]
            _insert(cur, engine, batch, table, d, pk, [("order_id", orders_present, "oltp.orders")] + extra, results)

        mql = rd(MKT / "olist_marketing_qualified_leads_dataset.csv")
        deals = rd(MKT / "olist_closed_deals_dataset.csv")
        have_deals = _existing(cur, "crm.closed_deals", ["mql_id"])
        d_ts = pd.to_datetime(deals["won_date"], errors="coerce")
        new_deals = deals[(d_ts < end) & d_ts.notna() & ~deals["mql_id"].isin(have_deals)]
        m_ts = pd.to_datetime(mql["first_contact_date"], errors="coerce")
        want_mql = ((m_ts < end) & m_ts.notna()) | mql["mql_id"].isin(set(new_deals["mql_id"]))      # parents of the new deals come along
        new_mql = mql[want_mql & ~mql["mql_id"].isin(have["crm.mql"])]
        _insert(cur, engine, batch, "crm.mql", new_mql, ["mql_id"], [], results)
        mql_present = have["crm.mql"] | set(new_mql["mql_id"])
        _insert(cur, engine, batch, "crm.closed_deals", new_deals, ["mql_id"], [("mql_id", mql_present, "crm.mql")], results)

        cur.execute("INSERT INTO etl_log.watermark (source_table, last_value, updated_at) VALUES (%s, %s, now()) "
                    "ON CONFLICT (source_table) DO UPDATE SET last_value = EXCLUDED.last_value, updated_at = now()", (WM, until_ts.to_pydatetime()))
        raw.commit()
    except BaseException:
        raw.rollback()
        print("Simulation failed: transaction rolled back, source unchanged.")
        raise
    finally:
        raw.close()
    total = sum(r["rows"] for r in results)
    secs = round(time.perf_counter() - t0, 1)
    print(f"simulate batch {batch}: source now complete up to {until_ts:%Y-%m-%d}; new rows " + ", ".join(f"{r['table'].split('.')[1]}={r['rows']:,}" for r in results)
          + f"; total {total:,} in {secs}s")
    return {"until": until_ts, "batch": batch, "rows": total, "tables": results, "seconds": secs, "skipped": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--until", help="insert records up to this date (default: end of the next month)")
    parser.add_argument("--database", default=config.DB_NAME)
    args = parser.parse_args()
    if args.database != config.DB_NAME:
        print(f"WARNING: simulating into {args.database}", file=sys.stderr)
    simulate(args.database, args.until)


if __name__ == "__main__":
    main()
