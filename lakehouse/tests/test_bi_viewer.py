"""The BI user (bi_viewer, used by Superset) can read only iceberg.gold and cannot write anywhere (Trino file-based access control, trino/rules.json)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from trino.dbapi import connect
from trino.exceptions import TrinoUserError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from lh_env import load_env  # noqa: E402

ENV = load_env()


def run(sql, user="bi_viewer"):
    cur = connect(host="127.0.0.1", port=int(ENV["LH_TRINO_PORT"]), user=user, catalog="iceberg", schema="gold").cursor()
    cur.execute(sql)
    return cur.fetchall()


def test_reads_gold():
    assert run("select count(*) from iceberg.gold.fact_order_item")[0][0] == 112650


@pytest.mark.parametrize("table", ["silver.orders", "bronze.oltp_orders", "ops.reconciliation"])
def test_cannot_read_other_layers(table):
    with pytest.raises(TrinoUserError, match="Access Denied"):
        run(f"select count(*) from iceberg.{table}")


@pytest.mark.parametrize("sql", ["delete from iceberg.gold.dim_order_status where false", "drop table iceberg.gold.dim_order_status",
                                 "create table iceberg.gold.zz_bi as select 1 as x"])
def test_cannot_write(sql):
    with pytest.raises(TrinoUserError, match="Access Denied"):
        run(sql)


def test_other_users_unaffected():
    assert run("select count(*) from iceberg.silver.orders", user="pytest")[0][0] == 99441
