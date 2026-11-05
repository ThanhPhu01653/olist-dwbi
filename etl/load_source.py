"""Load the Kaggle CSV files into the two simulated source systems (oltp, crm).

    python -m etl.load_source --initial                        # records up to 2017-12-31 -> DB_NAME (olist_dw)
    python -m etl.load_source --full --database olist_full     # everything -> olist_full (for EDA)
    python -m etl.load_source --report [--database NAME]       # only print row counts

The source is loaded "as is": no cleaning, only type conversion done by PostgreSQL COPY.
Rows that violate a key / foreign key / NOT NULL are NOT loaded and are written to etl_log.rejected_rows.
Rows that are simply outside the initial-load window (after the cutoff) are counted as "skipped": they are
reserved for etl.simulate_increment and are not errors.
Every run starts with TRUNCATE of the oltp + crm tables, so re-running gives the same result.
"""
from __future__ import annotations

import argparse
import io
import sys
import time
from dataclasses import dataclass, field
from typing import Callable

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from . import config
from .db import get_engine
from .log import JobRun, job_run, new_batch_id

ECOM, MKT = config.RAW_ECOMMERCE_DIR, config.RAW_MARKETING_DIR


@dataclass
class Ctx:
    initial: bool
    cutoff_end: pd.Timestamp                       # exclusive upper bound: day after the cutoff
    loaded: dict[str, set] = field(default_factory=dict)   # table -> loaded primary keys
    known: dict[str, set] = field(default_factory=dict)    # table -> all primary keys present in the CSV
    customers_in_scope: set = field(default_factory=set)


@dataclass
class Spec:
    table: str                                     # schema-qualified target table
    path: object                                   # CSV path
    pk: list[str]
    fks: list[tuple[str, str]] = field(default_factory=list)   # (column, parent table); parent pk is single-column
    # scope(df, ctx) -> (in_scope_mask, invalid_mask, invalid_reason); None = everything is in scope
    scope: Callable | None = None
    stream: bool = False                           # stream file straight into COPY (big table, no checks)


def _scope_by_date(column: str) -> Callable:
    def scope(df: pd.DataFrame, ctx: Ctx):
        ts = pd.to_datetime(df[column], errors="coerce")
        invalid = ts.isna()
        in_scope = (ts < ctx.cutoff_end) if ctx.initial else pd.Series(True, index=df.index)
        return in_scope & ~invalid, invalid, f"missing or unparsable {column}"
    return scope


def _scope_customers(df: pd.DataFrame, ctx: Ctx):
    # customer_id is generated per order, so a customer exists in the source only once it has placed an order.
    in_scope = df["customer_id"].isin(ctx.customers_in_scope) if ctx.initial else pd.Series(True, index=df.index)
    return in_scope, pd.Series(False, index=df.index), ""


# Parents first. Reference tables are loaded in full; orders/MQL define the window in the initial load.
SPECS = [
    Spec("oltp.product_category_name_translation", ECOM / "product_category_name_translation.csv", ["product_category_name"]),
    Spec("oltp.products", ECOM / "olist_products_dataset.csv", ["product_id"]),
    Spec("oltp.sellers", ECOM / "olist_sellers_dataset.csv", ["seller_id"]),
    Spec("oltp.geolocation", ECOM / "olist_geolocation_dataset.csv", [], stream=True),
    Spec("oltp.customers", ECOM / "olist_customers_dataset.csv", ["customer_id"], scope=_scope_customers),
    Spec("oltp.orders", ECOM / "olist_orders_dataset.csv", ["order_id"], [("customer_id", "oltp.customers")],
         scope=_scope_by_date("order_purchase_timestamp")),
    Spec("oltp.order_items", ECOM / "olist_order_items_dataset.csv", ["order_id", "order_item_id"],
         [("order_id", "oltp.orders"), ("product_id", "oltp.products"), ("seller_id", "oltp.sellers")]),
    Spec("oltp.order_payments", ECOM / "olist_order_payments_dataset.csv", ["order_id", "payment_sequential"],
         [("order_id", "oltp.orders")]),
    Spec("oltp.order_reviews", ECOM / "olist_order_reviews_dataset.csv", ["review_id", "order_id"],
         [("order_id", "oltp.orders")]),
    Spec("crm.mql", MKT / "olist_marketing_qualified_leads_dataset.csv", ["mql_id"],
         scope=_scope_by_date("first_contact_date")),
    Spec("crm.closed_deals", MKT / "olist_closed_deals_dataset.csv", ["mql_id"], [("mql_id", "crm.mql")],
         scope=_scope_by_date("won_date")),
]
TABLE_NAMES = [s.table for s in SPECS]


def check_files() -> None:
    missing = [s.path for s in SPECS if not s.path.exists()]
    if missing:
        lines = "\n".join(f"  - {p.relative_to(config.ROOT)}" for p in missing)
        sys.exit(
            f"Missing {len(missing)} of {len(SPECS)} CSV files:\n{lines}\n"
            "Download the two Kaggle datasets (olistbr/brazilian-ecommerce -> data/raw/ecommerce/, "
            "olistbr/marketing-funnel-olist -> data/raw/marketing/)."
        )
    print(f"CSV check: all {len(SPECS)} files found.")


def db_columns(cur, table: str) -> tuple[list[str], list[str]]:
    """(insertable columns in order, columns that must be non-empty) for a table."""
    schema, name = table.split(".")
    cur.execute(
        "SELECT column_name, is_nullable, column_default IS NOT NULL OR is_identity = 'YES' AS has_default, "
        "is_generated = 'ALWAYS' OR identity_generation = 'ALWAYS' AS generated "
        "FROM information_schema.columns WHERE table_schema = %s AND table_name = %s ORDER BY ordinal_position",
        (schema, name),
    )
    rows = cur.fetchall()
    insertable = [r[0] for r in rows if not r[3]]
    required = [r[0] for r in rows if r[1] == "NO" and not r[2]]
    return insertable, required


def copy_df(cur, table: str, df: pd.DataFrame, cols: list[str]) -> None:
    buf = io.StringIO()
    df[cols].to_csv(buf, index=False, header=False, lineterminator="\n")
    buf.seek(0)
    cur.copy_expert(f"COPY {table} ({', '.join(cols)}) FROM STDIN WITH (FORMAT csv, NULL '')", buf)


def load_stream(cur, spec: Spec, cols_db: list[str]) -> int:
    """Stream a CSV file straight into COPY (used for the 1M-row geolocation file)."""
    with open(spec.path, "r", encoding="utf-8", newline="") as fh:
        header = fh.readline().strip().replace('"', "").split(",")
        if header != cols_db:
            sys.exit(f"{spec.path.name}: header {header} does not match table columns {cols_db}")
        fh.seek(0)
        cur.copy_expert(f"COPY {spec.table} ({', '.join(header)}) FROM STDIN WITH (FORMAT csv, HEADER true, NULL '')", fh)
    return cur.rowcount


def load_table(cur, engine: Engine, batch_id: int, spec: Spec, ctx: Ctx) -> dict:
    t0 = time.perf_counter()
    cols_db, required = db_columns(cur, spec.table)
    with job_run(engine, batch_id, f"load_source.{spec.table}", "source", spec.table) as run:
        if spec.stream:
            n = load_stream(cur, spec, cols_db)
            run.rows_read = run.rows_inserted = n
            return _result(spec, n, n, 0, 0, time.perf_counter() - t0)

        df = pd.read_csv(spec.path, dtype=str, keep_default_na=False, encoding="utf-8")
        if set(df.columns) != set(cols_db):
            sys.exit(f"{spec.path.name}: CSV columns {list(df.columns)} do not match table columns {cols_db}")
        df = df[cols_db]
        run.rows_read = n_read = len(df)
        if len(spec.pk) == 1:
            ctx.known[spec.table] = set(df[spec.pk[0]])

        # 1. rows that cannot be judged: empty required column or unparsable filter column
        bad_required = pd.Series(False, index=df.index)
        for col in required:
            mask = df[col] == ""
            if mask.any():
                run.log_rejected(spec.table, f"NOT NULL column {col} is empty", df[mask])
                bad_required |= mask
        df = df[~bad_required]

        # 2. scope window (initial load) and unparsable dates
        skipped = 0
        if spec.scope is not None:
            in_scope, invalid, reason = spec.scope(df, ctx)
            if invalid.any():
                run.log_rejected(spec.table, reason, df[invalid])
            skipped += int((~in_scope & ~invalid).sum())
            df = df[in_scope]

        # 3. duplicate primary key (keep first occurrence)
        if spec.pk:
            dup = df.duplicated(spec.pk, keep="first")
            if dup.any():
                run.log_rejected(spec.table, f"duplicate primary key ({', '.join(spec.pk)})", df[dup])
                df = df[~dup]

        # 4. foreign keys: parent loaded -> ok; parent exists but is outside the window -> skipped; else orphan
        for col, parent in spec.fks:
            ok = df[col].isin(ctx.loaded[parent])
            outside = ~ok & df[col].isin(ctx.known[parent])
            orphan = ~ok & ~outside
            if orphan.any():
                run.log_rejected(spec.table, f"orphan: {col} not found in {parent}", df[orphan])
            skipped += int(outside.sum())
            df = df[ok]

        copy_df(cur, spec.table, df, cols_db)
        run.rows_inserted = len(df)
        run.message = f"skipped_outside_window={skipped}"
        if len(spec.pk) == 1:
            ctx.loaded[spec.table] = set(df[spec.pk[0]])
        return _result(spec, n_read, len(df), skipped, run.rows_rejected, time.perf_counter() - t0)


def _result(spec: Spec, n_read: int, loaded: int, skipped: int, rejected: int, secs: float) -> dict:
    return {"table": spec.table, "csv_rows": n_read, "loaded": loaded, "skipped": skipped,
            "rejected": rejected, "seconds": round(secs, 1)}


def table_counts(engine: Engine) -> pd.DataFrame:
    """Row count and column count of every source table in the connected database."""
    rows = []
    with engine.connect() as conn:
        for t in TABLE_NAMES:
            schema, name = t.split(".")
            n = conn.execute(text(f"SELECT count(*) FROM {t}")).scalar_one()
            c = conn.execute(
                text("SELECT count(*) FROM information_schema.columns WHERE table_schema = :s AND table_name = :t"),
                {"s": schema, "t": name},
            ).scalar_one()
            rows.append({"table": t, "rows": n, "columns": c})
    return pd.DataFrame(rows)


def run_load(mode: str, database: str) -> None:
    check_files()
    engine = get_engine(database)
    with engine.connect() as conn:
        if conn.execute(text("SELECT to_regclass('etl_log.job_run') IS NOT NULL")).scalar_one() is False:
            sys.exit(f"Database {database} is not initialised. Run: python -m etl.setup_db")

    ctx = Ctx(initial=(mode == "initial"), cutoff_end=pd.Timestamp(config.INITIAL_CUTOFF) + pd.Timedelta(days=1))
    if ctx.initial:
        orders = pd.read_csv(ECOM / "olist_orders_dataset.csv", dtype=str, keep_default_na=False,
                             usecols=["customer_id", "order_purchase_timestamp"])
        ts = pd.to_datetime(orders["order_purchase_timestamp"], errors="coerce")
        ctx.customers_in_scope = set(orders.loc[ts < ctx.cutoff_end, "customer_id"])

    batch_id = new_batch_id(engine)
    print(f"Batch {batch_id}: mode={mode}, database={database}"
          + (f", cutoff={config.INITIAL_CUTOFF}" if ctx.initial else ""))
    t0 = time.perf_counter()
    raw = engine.raw_connection()
    results = []
    try:
        with raw.cursor() as cur:
            cur.execute(f"TRUNCATE {', '.join(TABLE_NAMES)} RESTART IDENTITY CASCADE")
            for spec in SPECS:
                res = load_table(cur, engine, batch_id, spec, ctx)
                results.append(res)
                print(f"  {res['table']:42s} {res['loaded']:>9,} rows  ({res['seconds']}s)")
        raw.commit()
    except BaseException:
        raw.rollback()
        print("Load failed: transaction rolled back, source tables unchanged.")
        raise
    finally:
        raw.close()
    print(f"Done in {time.perf_counter() - t0:.1f}s\n")

    summary = pd.DataFrame(results).set_index("table")
    counts = table_counts(engine).set_index("table")
    summary["db_rows"] = counts["rows"]
    summary["db_columns"] = counts["columns"]
    print(summary.to_string(formatters={c: "{:,}".format for c in ["csv_rows", "loaded", "skipped", "rejected", "db_rows"]}))
    total_rej = int(summary["rejected"].sum())
    print(f"\nRejected rows logged in etl_log.rejected_rows: {total_rej:,} (batch {batch_id})")
    if (summary["loaded"] != summary["db_rows"]).any():
        sys.exit("Internal error: loaded row count differs from database row count.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--initial", action="store_true", help=f"load records up to {config.INITIAL_CUTOFF}")
    group.add_argument("--full", action="store_true", help="load every record (for EDA)")
    group.add_argument("--report", action="store_true", help="only print row counts")
    parser.add_argument("--database", help="target database (default: DB_NAME for --initial, DB_NAME_FULL for --full)")
    args = parser.parse_args()

    if args.report:
        database = args.database or config.DB_NAME
        print(f"Database {database}:")
        print(table_counts(get_engine(database)).to_string(index=False, formatters={"rows": "{:,}".format}))
        return
    mode = "initial" if args.initial else "full"
    database = args.database or (config.DB_NAME if args.initial else config.DB_NAME_FULL)
    if mode == "full" and database == config.DB_NAME:
        print(f"WARNING: loading the FULL data set into the main warehouse database {database}.")
    run_load(mode, database)


if __name__ == "__main__":
    main()
