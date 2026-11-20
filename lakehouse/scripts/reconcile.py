"""Reconcile the Lakehouse Gold (read through Trino) with the warehouse of chapter 3 (olist_dw.dw.*, PostgreSQL) table by table.

    python lakehouse/scripts/reconcile.py [--md handoff/FILE.md] [--no-ops] [--only dim_seller,fact_payment]

For each of the 16 tables (10 dimensions, 6 facts) it compares
  rows            number of rows
  sums            the sum of every numeric measure (money, counts, intervals) of the table
  key checksum    md5 over the sorted natural keys (order_id|order_item_id, mql_id, seller_id, ...)
  content checksum  md5 over the sorted full business content of every row. Surrogate keys differ between the two systems (they are numbered by
                  load order), so every foreign key is translated back to the natural value of the dimension row it points to
                  (customer = customer_unique_id + effective_from, product = product_id, ...): a fact row only matches when it resolves to the SAME
                  dimension members. Timestamps are covered through their date keys.
and the headline figure GMV = sum(price) of the items whose order is not in the status group Failed (13.494.400,74 BRL).
Both sides are queried with the same SQL text (placeholders for the schema), so the two checksums are computed identically.
Writes the result to iceberg.ops.reconciliation (one row per table and run) and, with --md, to a markdown table for the handoff. Exit code 1 if anything differs.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import psycopg2
from trino.dbapi import connect as trino_connect

from lh_env import ROOT, load_env

sys.path.insert(0, str(ROOT))
from etl import config  # noqa: E402

PG_S, TR_S = "dw", "iceberg.gold"
V = lambda c: f"coalesce(cast({c} as varchar), '~')"           # NULL -> '~' so that positions never shift
# doubles (latitude, longitude): the same cut on both sides, floor(x * 10^6) as an integer. round() would differ by 1e-6 on a few zips: PostgreSQL turns the double
# into numeric with 15 significant digits before rounding, Trino rounds the binary value.
DEC = lambda c, n=6: {"pg": f"cast(floor(({c}) * 1000000) as bigint)", "tr": f"cast(floor(({c}) * 1000000) as bigint)"}
# numerics whose scale differs between the systems (PostgreSQL: unconstrained numeric, Trino: decimal(p, s)): print both with 4 decimals
NUM4 = lambda c: {"pg": f"round(({c})::numeric, 4)", "tr": f"cast({c} as decimal(24, 4))"}


def cols(*names, alias="t"):
    return " || '|' || ".join(V(f"{alias}.{n}") for n in names)


def row_expr(base_cols, extra=()):
    parts = [V(f"t.{c}") for c in base_cols] + list(extra)
    return " || '|' || ".join(parts)


# ---------------------------------------------------------------------------------------------------- table definitions
# key: natural key; content: expression(s) over t (the table) and the joined dimensions; joins: SQL join text ({S} = schema); sums: numeric columns
CUST = "{S}.dim_customer dc on dc.customer_key = t.customer_key"
DEFS = {
    "dim_date": dict(key=["date_key"], content=["date_key", "full_date", "day_of_month", "day_of_week", "day_name", "week_of_year", "month", "month_name", "quarter", "year", "year_month",
                                                  "year_quarter", "is_weekend", "is_holiday_br", "holiday_name", "is_black_friday", "usd_brl", "ipca_index", "is_holiday_official",
                                                  "holiday_name_official"], sums=["day_of_month", "week_of_year", "usd_brl", "ipca_index"]),
    "dim_geography": dict(key=["zip_code_prefix"], content=["zip_code_prefix", "city", "state_code", "state_name", "region", "country", "ibge_municipio_code", "microrregiao",
                                                              "mesorregiao", "populacao_2016", "populacao_2017", "populacao_2018", "match_method"],
                          dec=["latitude", "longitude"], sums=["populacao_2017"], sum_dec=["latitude", "longitude"],
                          known=dict(col="city", where="t.zip_code_prefix in ('13848', '35348')",
                                     why="mode() of the city over the points of the zip is an exact tie (97 vs 97 points: 'mogi-guacu' / 'mogi guacu', and the same for "
                                         "pingo-d'agua / pingo-d agua). PostgreSQL breaks the tie with the sort order of its locale (hyphen before space), Spark with the code point "
                                         "order (space before hyphen). Not reproducible without copying the collation of the Windows PostgreSQL; chapter 3 is not changed.")),
    "dim_customer": dict(key=["customer_unique_id", "effective_from"], joins=["left join {S}.dim_geography g on g.geography_key = t.geography_key"],
                         content=["customer_unique_id", "zip_code_prefix", "city", "state_code", "effective_from", "effective_to", "is_current", "version_no"], extra=["g.zip_code_prefix"],
                         sums=["version_no"]),
    "dim_seller": dict(key=["seller_id"], joins=["left join {S}.dim_geography g on g.geography_key = t.geography_key"],
                       content=["seller_id", "zip_code_prefix", "city", "state_code", "is_from_funnel", "mql_id", "acquisition_origin", "acquisition_channel", "business_segment",
                                "lead_type", "business_type", "won_date", "first_sale_date"], extra=["g.zip_code_prefix"], sums=[]),
    "dim_product": dict(key=["product_id"], content=["product_id", "category_name_pt", "category_name_en", "category_group", "weight_g", "length_cm", "height_cm", "width_cm", "volume_cm3",
                                                       "size_class", "photos_qty", "name_length", "description_length"], sums=["weight_g", "volume_cm3", "photos_qty"]),
    "dim_order_status": dict(key=["order_status"], content=["order_status", "status_group", "is_final"], sums=[]),
    "dim_payment_type": dict(key=["payment_type"], content=["payment_type", "payment_group", "display_name"], sums=[]),
    "dim_lead_origin": dict(key=["origin"], content=["origin", "channel_group"], sums=[]),
    "dim_lead_profile": dict(key=["business_segment", "lead_type", "lead_behaviour_profile", "business_type", "has_company", "has_gtin", "average_stock"],
                             content=["business_segment", "lead_type", "lead_behaviour_profile", "business_type", "has_company", "has_gtin", "average_stock"], sums=[]),
    "dim_sales_rep": dict(key=["rep_id", "rep_role"], content=["rep_id", "rep_role"], sums=[]),

    "fact_order_item": dict(
        joins=["left join " + CUST, "left join {S}.dim_seller s on s.seller_key = t.seller_key", "left join {S}.dim_product p on p.product_key = t.product_key",
               "left join {S}.dim_order_status os on os.order_status_key = t.order_status_key", "left join {S}.dim_geography cg on cg.geography_key = t.customer_geography_key",
               "left join {S}.dim_geography sg on sg.geography_key = t.seller_geography_key"],
        key=["order_id", "order_item_id"],
        content=["order_id", "order_item_id", "purchase_date_key", "shipping_limit_date_key", "price", "freight_value", "item_total"],
        extra=["dc.customer_unique_id", "dc.effective_from", "s.seller_id", "p.product_id", "os.order_status", "cg.zip_code_prefix", "sg.zip_code_prefix"],
        sums=["price", "freight_value", "item_total"], money="price"),
    "fact_payment": dict(
        joins=["left join " + CUST, "left join {S}.dim_payment_type pt on pt.payment_type_key = t.payment_type_key"],
        key=["order_id", "payment_sequential"], content=["order_id", "payment_sequential", "purchase_date_key", "payment_installments", "payment_value"],
        extra=["dc.customer_unique_id", "dc.effective_from", "pt.payment_type"], sums=["payment_value", "payment_installments"], money="payment_value"),
    "fact_order_fulfillment": dict(
        joins=["left join " + CUST, "left join {S}.dim_order_status os on os.order_status_key = t.order_status_key", "left join {S}.dim_geography cg on cg.geography_key = t.customer_geography_key"],
        key=["order_id"],
        content=["order_id", "purchase_date_key", "approved_date_key", "carrier_date_key", "delivered_date_key", "estimated_date_key", "approval_hours", "handling_days", "transit_days",
                 "lead_days", "delay_days", "promised_days", "is_delivered", "is_late", "is_canceled", "item_count", "seller_count", "order_value", "freight_total", "payment_total", "dq_flag_count"],
        extra=["dc.customer_unique_id", "dc.effective_from", "os.order_status", "cg.zip_code_prefix"],
        sums=["order_value", "freight_total", "payment_total", "approval_hours", "handling_days", "transit_days", "lead_days", "delay_days", "promised_days", "item_count", "seller_count",
              "is_delivered", "is_late", "is_canceled", "dq_flag_count"], money="order_value"),
    "fact_review": dict(
        joins=["left join " + CUST], key=["review_id", "order_id"],
        content=["review_id", "order_id", "review_creation_date_key", "review_answer_date_key", "review_score", "is_negative", "has_comment_title", "has_comment_message", "comment_length",
                 "response_hours", "delivered_late", "is_delivered"], extra=["dc.customer_unique_id", "dc.effective_from"],
        sums=["review_score", "is_negative", "has_comment_title", "has_comment_message", "comment_length", "response_hours", "delivered_late", "is_delivered"]),
    "fact_lead_funnel": dict(
        joins=["left join {S}.dim_lead_origin lo on lo.lead_origin_key = t.lead_origin_key", "left join {S}.dim_lead_profile lp on lp.lead_profile_key = t.lead_profile_key",
               "left join {S}.dim_seller s on s.seller_key = t.seller_key", "left join {S}.dim_sales_rep sdr on sdr.sales_rep_key = t.sdr_key", "left join {S}.dim_sales_rep sr on sr.sales_rep_key = t.sr_key"],
        key=["mql_id"],
        content=["mql_id", "landing_page_id", "first_contact_date_key", "won_date_key", "first_sale_date_key", "is_won", "has_first_sale", "days_to_close", "days_won_to_first_sale",
                 "declared_product_catalog_size", "declared_monthly_revenue", "seller_gmv_first_90d"],
        extra=["lo.origin", "lp.business_segment", "lp.lead_type", "lp.lead_behaviour_profile", "lp.business_type", "lp.has_company", "lp.has_gtin", "lp.average_stock", "s.seller_id",
               "sdr.rep_id", "sr.rep_id"],
        sums=["is_won", "has_first_sale", "days_to_close", "days_won_to_first_sale", "declared_product_catalog_size", "declared_monthly_revenue", "seller_gmv_first_90d"]),
    "fact_seller_monthly": dict(
        joins=["left join {S}.dim_seller s on s.seller_key = t.seller_key"], key=["month_date_key", "seller_id"],
        key_extra=["s.seller_id"],
        content=["month_date_key", "orders", "items", "gmv", "freight", "delivered_orders", "late_orders", "late_rate", "canceled_orders", "avg_review_score", "is_active", "months_since_first_sale"],
        extra=["s.seller_id"], sums=["orders", "items", "gmv", "freight", "delivered_orders", "late_orders", "late_rate", "canceled_orders", "avg_review_score", "is_active", "months_since_first_sale"],
        money="gmv", num4=["late_rate", "avg_review_score"]),
}


def dialect(text: str, which: str) -> str:
    return text.replace("{S}", PG_S if which == "pg" else TR_S)


def md5_agg(row_sql: str, which: str) -> str:
    if which == "pg":
        return f"md5(string_agg(r, chr(10) order by r collate \"C\"))"
    return "lower(to_hex(md5(to_utf8(array_join(array_sort(array_agg(r)), chr(10))))))"


def build_sql(name: str, d: dict, which: str) -> dict:
    """The queries (count + sums, key checksum, content checksum) of one table for one dialect."""
    joins = " ".join(dialect(j, which) for j in d.get("joins", []))
    base = f"{PG_S if which == 'pg' else TR_S}.{name} t {joins}"
    # key
    key_cols = [k for k in d["key"] if k != "seller_id" or "key_extra" not in d]
    key_parts = [V(f"t.{k}") for k in key_cols] + [V(e) for e in d.get("key_extra", [])]
    key_row = " || '|' || ".join(key_parts)
    n4 = d.get("num4", [])

    def content_of(skip=None):
        parts = [V(f"t.{c}") if c not in n4 else f"coalesce(cast({NUM4('t.' + c)[which]} as varchar), '~')" for c in d["content"] if c != skip]
        for dc in d.get("dec", []):
            parts.append(f"coalesce(cast({DEC('t.' + dc)[which]} as varchar), '~')")
        parts += [V(e) for e in d.get("extra", [])]
        return " || '|' || ".join(parts)

    content_row = content_of()
    known = d.get("known")
    sums = [f"coalesce(cast(sum(t.{c}) as varchar), '~')" if c not in n4 else f"coalesce(cast({NUM4('sum(t.' + c + ')')[which]} as varchar), '~')" for c in d.get("sums", [])]
    for c in d.get("sum_dec", []):
        sums.append(f"coalesce(cast(sum({DEC('t.' + c)[which]}) as varchar), '~')")
    sum_sql = " || ';' || ".join(sums) if sums else "''"
    return {
        "count": f"select count(*) from {base}",
        "sums": f"select {sum_sql} from {base}",
        "key": f"select {md5_agg('r', which)} from (select {key_row} as r from {base}) x",
        "content": f"select {md5_agg('r', which)} from (select {content_row} as r from {base}{(' where not (' + known['where'] + ')') if known else ''}) x",
        "content_known": (f"select {md5_agg('r', which)} from (select {content_of(known['col'])} as r from {base} where {known['where']}) x" if known else None),
        "known_values": (f"select {md5_agg('r', which)} from (select {V('t.' + known['col'])} as r from {base} where {known['where']}) x" if known else None),
        "money": (f"select cast(sum(t.{d['money']}) as varchar) from {base}" if "money" in d else None),
    }


def one(cur, sql):
    cur.execute(sql)
    return cur.fetchone()[0]


GMV_SQL = {
    "pg": "select cast(sum(f.price) as varchar) from dw.fact_order_item f join dw.dim_order_status s on s.order_status_key = f.order_status_key and s.status_group <> 'Failed'",
    "tr": "select cast(sum(f.price) as varchar) from iceberg.gold.fact_order_item f join iceberg.gold.dim_order_status s on s.order_status_key = f.order_status_key and s.status_group <> 'Failed'",
}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--md")
    ap.add_argument("--no-ops", action="store_true")
    ap.add_argument("--only")
    a = ap.parse_args()
    env = load_env()
    pg = psycopg2.connect(host=config.DB_HOST, port=config.DB_PORT, user=config.DB_USER, password=config.db_password(), dbname=config.DB_NAME)
    pgc = pg.cursor()
    tr = trino_connect(host="127.0.0.1", port=int(env["LH_TRINO_PORT"]), user="reconcile", catalog="iceberg", schema="gold")
    trc = tr.cursor()
    names = [n for n in DEFS if not a.only or n in a.only.split(",")]
    rows = []
    for name in names:
        t0 = time.perf_counter()
        d = DEFS[name]
        q = {w: build_sql(name, d, w) for w in ("pg", "tr")}
        res = {}
        for w, cur in (("pg", pgc), ("tr", trc)):
            res[w] = {k: (one(cur, v) if v else None) for k, v in q[w].items()}
        ok_rows = int(res["pg"]["count"]) == int(res["tr"]["count"])
        ok_sums = res["pg"]["sums"] == res["tr"]["sums"]
        ok_key = res["pg"]["key"] == res["tr"]["key"]
        ok_content = res["pg"]["content"] == res["tr"]["content"] and res["pg"]["content_known"] == res["tr"]["content_known"]
        known = d.get("known")
        known_differs = bool(known) and res["pg"]["known_values"] != res["tr"]["known_values"]
        rows.append(dict(table=name, dw_rows=int(res["pg"]["count"]), gold_rows=int(res["tr"]["count"]), dw_money=res["pg"]["money"], gold_money=res["tr"]["money"],
                         ok_rows=ok_rows, ok_sums=ok_sums, ok_key=ok_key, ok_content=ok_content, known=known, known_differs=known_differs, pg=res["pg"], tr=res["tr"], seconds=round(time.perf_counter() - t0, 1)))
        r = rows[-1]
        print(f"{name:24} rows {r['dw_rows']:>8,} / {r['gold_rows']:>8,} {'OK ' if ok_rows else 'DIFF'}  sums {'OK ' if ok_sums else 'DIFF'}  key {'OK ' if ok_key else 'DIFF'}  content {'OK ' if ok_content else 'DIFF'}  ({r['seconds']}s)", flush=True)
        if known:
            print(f"    explained exception: column {known['col']} of the rows where {known['where']} differs ({'yes' if known_differs else 'NO'}); every other column of those rows and every row outside them match")
        if not ok_sums:
            print("    sums dw  :", res["pg"]["sums"], "\n    sums gold:", res["tr"]["sums"])
    gmv_pg, gmv_tr = one(pgc, GMV_SQL["pg"]), one(trc, GMV_SQL["tr"])
    print(f"GMV (price of items whose order is not Failed): dw {gmv_pg}  gold {gmv_tr}  {'OK' if gmv_pg == gmv_tr else 'DIFF'}")
    all_ok = all(r["ok_rows"] and r["ok_sums"] and r["ok_key"] and r["ok_content"] for r in rows) and gmv_pg == gmv_tr
    print("RESULT:", "all tables match" if all_ok else "DIFFERENCES FOUND")

    if not a.no_ops:
        trc.execute("create schema if not exists iceberg.ops")
        trc.fetchall()
        trc.execute("""create table if not exists iceberg.ops.reconciliation (run_at timestamp(6), table_name varchar, dw_rows bigint, gold_rows bigint, dw_money varchar, gold_money varchar,
                       rows_match boolean, sums_match boolean, key_checksum_match boolean, content_checksum_match boolean, dw_content_md5 varchar, gold_content_md5 varchar,
                       note varchar)""")
        trc.fetchall()
        for r in rows:
            trc.execute("insert into iceberg.ops.reconciliation values (current_timestamp(6), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)" if False else
                        "insert into iceberg.ops.reconciliation values (cast(current_timestamp as timestamp(6)), '%s', %d, %d, %s, %s, %s, %s, %s, %s, '%s', '%s', %s)" % (
                            r["table"], r["dw_rows"], r["gold_rows"], ("'%s'" % r["dw_money"]) if r["dw_money"] else "null", ("'%s'" % r["gold_money"]) if r["gold_money"] else "null",
                            str(r["ok_rows"]).lower(), str(r["ok_sums"]).lower(), str(r["ok_key"]).lower(), str(r["ok_content"]).lower(), r["pg"]["content"], r["tr"]["content"],
                            ("'explained exception: %s in %s'" % (r["known"]["col"], r["known"]["where"].replace("'", "")) if r["known"] else "null")))
            trc.fetchall()
    if a.md:
        L = ["| Bảng | Số dòng kho | Số dòng Gold | Tổng tiền kho | Tổng tiền Gold | Tổng các số đo | Checksum khoá | Checksum nội dung |", "| --- | ---: | ---: | ---: | ---: | :---: | :---: | :---: |"]
        n = lambda x: f"{x:,}".replace(",", ".")
        for r in rows:
            L.append(f"| `{r['table']}` | {n(r['dw_rows'])} | {n(r['gold_rows'])} | {r['dw_money'] or '–'} | {r['gold_money'] or '–'} | {'khớp' if r['ok_sums'] else 'LỆCH'} | {'khớp' if r['ok_key'] else 'LỆCH'} | {('khớp' if r['ok_content'] else 'LỆCH') + (' (trừ cột `%s` của 2 zip, xem dưới)' % r['known']['col'] if r['known'] else '')} |")
        L.append("")
        for r in rows:
            if r["known"]:
                L.append(f"Ngoại lệ có giải thích, `{r['table']}`: {r['known']['why']}")
                L.append("")
        L.append(f"GMV (Σ price của dòng hàng thuộc đơn không phải Failed): kho {gmv_pg}, Gold {gmv_tr}: {'khớp' if gmv_pg == gmv_tr else 'LỆCH'}.")
        Path(a.md).write_text("\n".join(L) + "\n", encoding="utf-8")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
