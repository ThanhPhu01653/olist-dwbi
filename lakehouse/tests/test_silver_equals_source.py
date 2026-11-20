"""Step 12 - the two mandatory checks that the logs cannot give (they caught the orphan / localCheckpoint bug of step 4):

  * Bronze = Kafka     : rows of every bronze.<schema>_<table> equal the end offset of its topic (the stream loses and duplicates nothing)
  * Silver = source    : for each source table, rows and an md5 of the sorted primary keys are the same in PostgreSQL (the CDC source) and in iceberg.silver,
                         and the *_rejected tables are empty
  * Silver geo = ODS   : silver.geolocation_zip has as many zips as ods.geolocation_zip of the chapter 3 warehouse

    python -m pytest lakehouse/tests -q          (stack up, stream stopped, replay finished)
The 71 dbt tests (Gold) and lakehouse/scripts/reconcile.py (Gold = warehouse, 16 tables) are the other checks; they are run by test_gold_and_reconcile.py when --run-slow is given.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import psycopg2
import pytest
from trino.dbapi import connect

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "lakehouse" / "scripts"))
sys.path.insert(0, str(ROOT))
from lh_env import load_env  # noqa: E402
from etl import config  # noqa: E402

ENV = load_env()

# source table -> (silver table, key columns)
TABLES = {
    "oltp.orders": ("orders", ["order_id"]),
    "oltp.customers": ("customers", ["customer_id"]),
    "oltp.order_items": ("order_items", ["order_id", "order_item_id"]),
    "oltp.order_payments": ("order_payments", ["order_id", "payment_sequential"]),
    "oltp.order_reviews": ("order_reviews", ["review_id", "order_id"]),
    "oltp.products": ("products", ["product_id"]),
    "oltp.sellers": ("sellers", ["seller_id"]),
    "oltp.product_category_name_translation": ("category_translation", ["product_category_name"]),
    "crm.mql": ("mql", ["mql_id"]),
    "crm.closed_deals": ("closed_deals", ["mql_id"]),
}
REJECTED = ["orders", "customers", "order_items", "order_payments", "order_reviews", "closed_deals"]


@pytest.fixture(scope="module")
def src():
    c = psycopg2.connect(host="127.0.0.1", port=int(ENV["LH_PG_PORT"]), user=ENV["LH_PG_USER"], password=ENV["LH_PG_PASSWORD"], dbname=ENV["LH_PG_DB"])
    yield c
    c.close()


@pytest.fixture(scope="module")
def tr():
    return connect(host="127.0.0.1", port=int(ENV["LH_TRINO_PORT"]), user="pytest", catalog="iceberg", schema="silver")


def trino_one(tr, sql):
    cur = tr.cursor()
    cur.execute(sql)
    return cur.fetchall()[0]


def pg_one(src, sql):
    with src.cursor() as c:
        c.execute(sql)
        return c.fetchone()


def key_expr(cols, side):
    parts = [f"rtrim(cast({c} as varchar))" if side == "pg" else f"cast({c} as varchar)" for c in cols]
    return " || '|' || ".join(parts)


@pytest.mark.parametrize("source_table", list(TABLES))
def test_silver_equals_source(src, tr, source_table):
    silver, keys = TABLES[source_table]
    k_pg, k_tr = key_expr(keys, "pg"), key_expr(keys, "tr")
    n_src, md5_src = pg_one(src, f"select count(*), md5(string_agg({k_pg}, ',' order by {k_pg})) from {source_table}")
    n_sil, md5_sil = trino_one(tr, f"select count(*), lower(to_hex(md5(to_utf8(array_join(array_sort(array_agg({k_tr})), ',')))))  from iceberg.silver.{silver}")
    assert n_sil == n_src, f"{silver}: rows Silver {n_sil} vs source {n_src}"
    assert md5_sil == md5_src, f"{silver}: key checksum differs although the row counts are equal"


@pytest.mark.parametrize("name", REJECTED)
def test_rejected_tables_are_empty(tr, name):
    assert trino_one(tr, f"select count(*) from iceberg.silver.{name}_rejected")[0] == 0, f"{name}_rejected still holds rows (orphans never resolved or rejected by a rule)"


def test_bronze_equals_kafka():
    """Rows of each Bronze table = sum of the end offsets of its topic (topics have one partition each)."""
    out = subprocess.run(["docker", "exec", "lh-kafka", "/opt/kafka/bin/kafka-get-offsets.sh", "--bootstrap-server", "localhost:9092"], capture_output=True, text=True, check=True,
                         env={**__import__("os").environ, "MSYS_NO_PATHCONV": "1"}).stdout
    ends = {}
    for line in out.splitlines():
        parts = line.strip().split(":")
        if len(parts) == 3 and parts[0].startswith("olist."):
            ends[parts[0]] = ends.get(parts[0], 0) + int(parts[2])
    assert len(ends) == 11, f"expected 11 topics, found {len(ends)}"
    tr = connect(host="127.0.0.1", port=int(ENV["LH_TRINO_PORT"]), user="pytest", catalog="iceberg", schema="bronze")
    bad = []
    for topic, end in ends.items():
        table = "bronze." + topic.removeprefix("olist.").replace(".", "_")
        n = trino_one(tr, f"select count(*) from iceberg.{table}")[0]
        if n != end:
            bad.append(f"{table}: {n} rows vs offset {end}")
    assert not bad, "; ".join(bad)


def test_silver_geo_equals_ods(tr):
    dw = psycopg2.connect(host=config.DB_HOST, port=config.DB_PORT, user=config.DB_USER, password=config.db_password(), dbname=config.DB_NAME)
    with dw.cursor() as c:
        c.execute("select count(*) from ods.geolocation_zip")
        n_ods = c.fetchone()[0]
    dw.close()
    assert trino_one(tr, "select count(*) from iceberg.silver.geolocation_zip")[0] == n_ods
