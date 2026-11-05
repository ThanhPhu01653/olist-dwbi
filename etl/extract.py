"""Extract oltp/crm -> staging.stg_*  (python -m etl.extract --mode full|incremental).

full:        TRUNCATE staging, copy every source row.
incremental: only rows that are not in staging yet. orders by order_purchase_timestamp (>= watermark),
             child tables by the order_id of the orders staged in this batch; customers of the new orders;
             mql / closed_deals / sellers / products / geolocation / translation: every source row not yet staged (small tables).
             mql and closed_deals deliberately do NOT use a date watermark: the CRM can register a deal before the first contact
             date of its lead (won_date < first_contact_date), and a date filter would then skip the lead for ever.
Every table writes an etl_log.job_run row; the watermarks of orders / mql / closed_deals (max date staged) are kept in etl_log.watermark.
"""
from __future__ import annotations

import argparse

from sqlalchemy.engine import Engine

from . import config
from .db import get_engine
from .log import job_run, new_batch_id

# name -> (source table, key columns for the anti-join, how to select the incremental rows)
TABLES = [
    ("orders", "oltp.orders", ["order_id"], "wm_ts:order_purchase_timestamp"),
    ("customers", "oltp.customers", ["customer_id"], "new_orders:customer_id"),
    ("order_items", "oltp.order_items", ["order_id", "order_item_id"], "new_orders:order_id"),
    ("order_payments", "oltp.order_payments", ["order_id", "payment_sequential"], "new_orders:order_id"),
    ("order_reviews", "oltp.order_reviews", ["review_id", "order_id"], "new_orders:order_id"),
    ("sellers", "oltp.sellers", ["seller_id"], "all"),
    ("products", "oltp.products", ["product_id"], "all"),
    ("geolocation", "oltp.geolocation", ["id"], "all"),
    ("product_category_name_translation", "oltp.product_category_name_translation", ["product_category_name"], "all"),
    ("mql", "crm.mql", ["mql_id"], "all"),
    ("closed_deals", "crm.closed_deals", ["mql_id"], "all"),
]
WATERMARKS = {"orders": "order_purchase_timestamp", "mql": "first_contact_date", "closed_deals": "won_date"}


def _columns(cur, src: str) -> list[str]:
    schema, name = src.split(".")
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema=%s AND table_name=%s ORDER BY ordinal_position",
                (schema, name))
    return [r[0] for r in cur.fetchall()]


def extract(engine: Engine, batch_id: int, mode: str) -> list[dict]:
    results = []
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        if mode == "full":
            cur.execute("TRUNCATE " + ", ".join(f"staging.stg_{t[0]}" for t in TABLES))
            cur.execute("DELETE FROM etl_log.watermark WHERE source_table = ANY(%s)", ([f"staging.stg_{t}" for t in WATERMARKS],))
        for name, src, keys, how in TABLES:
            with job_run(engine, batch_id, f"extract.{name}", "staging", f"staging.stg_{name}") as run:
                cols = _columns(cur, src)
                col_list = ", ".join(cols)
                sel = ", ".join(f"o.{c}" for c in cols)
                where = "TRUE"
                params: dict = {"b": batch_id}
                if mode == "incremental":
                    anti = " AND ".join(f"t.{k} = o.{k}" for k in keys)
                    where = f"NOT EXISTS (SELECT 1 FROM staging.stg_{name} t WHERE {anti})"
                    if how.startswith("wm_ts:"):
                        col = how.split(":")[1]
                        cur.execute("SELECT last_value FROM etl_log.watermark WHERE source_table = %s", (f"staging.stg_{name}",))
                        row = cur.fetchone()
                        if row:
                            where += f" AND o.{col} >= %(wm)s::timestamptz::{'date' if name == 'mql' else 'timestamp'}"
                            params["wm"] = row[0]
                    elif how.startswith("new_orders:"):
                        col = how.split(":")[1]
                        where += f" AND o.{col} IN (SELECT s.{col} FROM staging.stg_orders s WHERE s.load_batch_id = %(b)s)"
                cur.execute(f"INSERT INTO staging.stg_{name} ({col_list}, load_batch_id) SELECT {sel}, %(b)s FROM {src} o WHERE {where}", params)
                run.rows_read = run.rows_inserted = cur.rowcount
                if name in WATERMARKS:
                    cur.execute(
                        f"INSERT INTO etl_log.watermark (source_table, last_value, updated_at) "
                        f"SELECT %s, max({WATERMARKS[name]})::timestamptz, now() FROM staging.stg_{name} "
                        f"ON CONFLICT (source_table) DO UPDATE SET last_value = EXCLUDED.last_value, updated_at = now()",
                        (f"staging.stg_{name}",))
                results.append({"table": f"stg_{name}", "rows": run.rows_inserted})
        raw.commit()
    except BaseException:
        raw.rollback()
        raise
    finally:
        raw.close()
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mode", choices=["full", "incremental"], default="full")
    parser.add_argument("--database", default=config.DB_NAME)
    args = parser.parse_args()
    engine = get_engine(args.database)
    batch = new_batch_id(engine)
    res = extract(engine, batch, args.mode)
    print(f"extract {args.mode} batch {batch}: " + ", ".join(f"{r['table']}={r['rows']:,}" for r in res))


if __name__ == "__main__":
    main()
