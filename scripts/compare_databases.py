"""Compare two warehouse databases table by table (row count, sum of the money measures, content checksum on NATURAL keys).

    python scripts/compare_databases.py --a olist_dw --b olist_full_check
Used to prove "incremental result = full result": A = olist_dw after all increments, B = a database loaded in one full run.
Surrogate keys differ between the two (identity order), so the checksum joins every key back to its natural key first.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text

from etl.db import get_engine

D = "to_char(%s, 'YYYY-MM-DD')"
# table -> (row expression text built from natural keys, FROM clause)
CHECKS = {
    "dim_date": ("concat_ws('|', d.date_key, d.full_date, d.is_holiday_br, d.holiday_name, d.is_black_friday)", "dw.dim_date d"),
    "dim_geography": ("concat_ws('|', d.zip_code_prefix, d.city, d.state_code, d.state_name, d.region, d.latitude, d.longitude)", "dw.dim_geography d"),
    "dim_customer": ("concat_ws('|', d.customer_unique_id, d.zip_code_prefix, d.city, d.state_code, d.effective_from, d.effective_to, d.is_current, d.version_no)", "dw.dim_customer d"),
    "dim_seller": ("concat_ws('|', d.seller_id, d.zip_code_prefix, d.city, d.is_from_funnel, d.mql_id, d.acquisition_origin, d.acquisition_channel, d.business_segment, d.lead_type, d.business_type, d.won_date, d.first_sale_date)", "dw.dim_seller d"),
    "dim_product": ("concat_ws('|', d.product_id, d.category_name_pt, d.category_name_en, d.category_group, d.weight_g, d.volume_cm3, d.size_class)", "dw.dim_product d"),
    "dim_order_status": ("concat_ws('|', d.order_status, d.status_group, d.is_final)", "dw.dim_order_status d"),
    "dim_payment_type": ("concat_ws('|', d.payment_type, d.payment_group, d.display_name)", "dw.dim_payment_type d"),
    "dim_lead_origin": ("concat_ws('|', d.origin, d.channel_group)", "dw.dim_lead_origin d"),
    "dim_lead_profile": ("concat_ws('|', d.business_segment, d.lead_type, d.lead_behaviour_profile, d.business_type, d.has_company, d.has_gtin, d.average_stock)", "dw.dim_lead_profile d"),
    "dim_sales_rep": ("concat_ws('|', d.rep_id, d.rep_role)", "dw.dim_sales_rep d"),
    "fact_order_item": ("concat_ws('|', f.order_id, f.order_item_id, dd.full_date, ds.full_date, c.customer_unique_id, c.effective_from, g1.zip_code_prefix, g2.zip_code_prefix, s.seller_id, p.product_id, os.order_status, f.price, f.freight_value, f.item_total)",
                        "dw.fact_order_item f JOIN dw.dim_date dd ON dd.date_key = f.purchase_date_key JOIN dw.dim_date ds ON ds.date_key = f.shipping_limit_date_key JOIN dw.dim_customer c USING (customer_key) "
                        "JOIN dw.dim_geography g1 ON g1.geography_key = f.customer_geography_key JOIN dw.dim_geography g2 ON g2.geography_key = f.seller_geography_key "
                        "JOIN dw.dim_seller s USING (seller_key) JOIN dw.dim_product p USING (product_key) JOIN dw.dim_order_status os USING (order_status_key)"),
    "fact_order_fulfillment": ("concat_ws('|', f.order_id, c.customer_unique_id, c.effective_from, g.zip_code_prefix, os.order_status, f.purchase_ts, f.approved_ts, f.carrier_ts, f.delivered_ts, f.estimated_ts, f.approval_hours, f.handling_days, f.transit_days, f.lead_days, f.delay_days, f.promised_days, f.is_delivered, f.is_late, f.is_canceled, f.item_count, f.seller_count, f.order_value, f.freight_total, f.payment_total, f.dq_flag_count, f.purchase_date_key, f.approved_date_key, f.carrier_date_key, f.delivered_date_key, f.estimated_date_key)",
                               "dw.fact_order_fulfillment f JOIN dw.dim_customer c USING (customer_key) JOIN dw.dim_geography g ON g.geography_key = f.customer_geography_key JOIN dw.dim_order_status os USING (order_status_key)"),
    "fact_payment": ("concat_ws('|', f.order_id, f.payment_sequential, f.purchase_date_key, c.customer_unique_id, c.effective_from, pt.payment_type, f.payment_installments, f.payment_value)",
                     "dw.fact_payment f JOIN dw.dim_customer c USING (customer_key) JOIN dw.dim_payment_type pt USING (payment_type_key)"),
    "fact_review": ("concat_ws('|', f.review_id, f.order_id, f.review_creation_date_key, f.review_answer_date_key, c.customer_unique_id, c.effective_from, f.review_score, f.is_negative, f.has_comment_title, f.has_comment_message, f.comment_length, f.response_hours, f.delivered_late, f.is_delivered)",
                    "dw.fact_review f JOIN dw.dim_customer c USING (customer_key)"),
    "fact_lead_funnel": ("concat_ws('|', f.mql_id, f.landing_page_id, f.first_contact_date_key, f.won_date_key, f.first_sale_date_key, lo.origin, lp.business_segment, lp.lead_type, lp.lead_behaviour_profile, lp.business_type, lp.has_company, lp.has_gtin, lp.average_stock, s.seller_id, sdr.rep_id, sr.rep_id, f.is_won, f.has_first_sale, f.days_to_close, f.days_won_to_first_sale, f.declared_product_catalog_size, f.declared_monthly_revenue, f.seller_gmv_first_90d)",
                         "dw.fact_lead_funnel f JOIN dw.dim_lead_origin lo USING (lead_origin_key) JOIN dw.dim_lead_profile lp USING (lead_profile_key) JOIN dw.dim_seller s USING (seller_key) "
                         "JOIN dw.dim_sales_rep sdr ON sdr.sales_rep_key = f.sdr_key JOIN dw.dim_sales_rep sr ON sr.sales_rep_key = f.sr_key"),
    "fact_seller_monthly": ("concat_ws('|', f.month_date_key, s.seller_id, f.orders, f.items, f.gmv, f.freight, f.delivered_orders, f.late_orders, f.late_rate, f.canceled_orders, f.avg_review_score, f.is_active, f.months_since_first_sale)",
                            "dw.fact_seller_monthly f JOIN dw.dim_seller s USING (seller_key)"),
}
MONEY = {"fact_order_item": "sum(f.price)", "fact_payment": "sum(f.payment_value)", "fact_order_fulfillment": "sum(f.order_value)", "fact_seller_monthly": "sum(f.gmv)"}


def measure(conn, table: str) -> tuple[int, str, str]:
    expr, frm = CHECKS[table]
    alias = "f" if table.startswith("fact") else "d"
    row = conn.execute(text(f"SELECT count(*), md5(string_agg(x, E'\\n' ORDER BY x)) FROM (SELECT {expr} AS x FROM {frm}) t")).one()
    money = conn.execute(text(f"SELECT {MONEY[table]} FROM {frm}")).scalar_one() if table in MONEY else None
    return row[0], row[1], "" if money is None else f"{money:,.2f}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--a", required=True)
    parser.add_argument("--b", required=True)
    args = parser.parse_args()
    ea, eb = get_engine(args.a), get_engine(args.b)
    bad = 0
    print(f"| Bảng | Số dòng {args.a} | Số dòng {args.b} | Tổng tiền | Checksum nội dung | Kết quả |")
    print("| --- | ---: | ---: | ---: | --- | --- |")
    with ea.connect() as ca, eb.connect() as cb:
        for t in CHECKS:
            na, ha, ma = measure(ca, t)
            nb, hb, mb = measure(cb, t)
            ok = (na, ha, ma) == (nb, hb, mb)
            bad += not ok
            print(f"| {t} | {na:,} | {nb:,} | {ma if ma == mb else ma + ' ≠ ' + mb} | {'khớp' if ha == hb else 'KHÁC'} | {'khớp' if ok else 'LỆCH'} |")
    print(f"\n{len(CHECKS) - bad}/{len(CHECKS)} bảng khớp hoàn toàn")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
