"""Follow ONE real order and ONE real MQL through every layer and write the real values into huong-dan/01-pipeline-bang-loi.md.

    python scripts/gen_trace_examples.py
The narrative of the file is hand-written; only the blocks between  <!-- TRACE_ORDER:START/END -->  and  <!-- TRACE_MQL:START/END -->  are generated.
Chosen order: delivered, 3 items, review, payment, customer with 2 SCD2 versions (the order belongs to the OLD version). Chosen MQL: won, seller has sales.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sqlalchemy import text

from etl import config
from etl.db import get_engine

ORDER_ID = "19c36691fd116059bf49b7960f1db743"


def cell(v) -> str:
    if v is None:
        return "*(trống)*"
    if isinstance(v, str):
        v = v.strip().replace("|", "/").replace("\n", " ")
        return v[:60] + ("…" if len(v) > 60 else "")
    if hasattr(v, "quantize"):
        return f"{v:,.2f}"
    return str(v)


def table(conn, sql: str, params: dict | None = None, vertical: bool = True) -> str:
    res = conn.execute(text(sql), params or {})
    cols, rows = list(res.keys()), res.fetchall()
    if not rows:
        return "*(không có dòng)*\n"
    if vertical and len(rows) == 1:
        return "| Cột | Giá trị |\n| --- | --- |\n" + "\n".join(f"| `{c}` | {cell(v)} |" for c, v in zip(cols, rows[0])) + "\n"
    return "| " + " | ".join(cols) + " |\n| " + " | ".join("---" for _ in cols) + " |\n" + "\n".join("| " + " | ".join(cell(v) for v in r) + " |" for r in rows) + "\n"


def sec(title: str, body: str) -> str:
    return f"**{title}**\n\n{body}\n"


def order_block(conn) -> str:
    p = {"o": ORDER_ID}
    cid = conn.execute(text("SELECT customer_id FROM oltp.orders WHERE order_id = :o"), p).scalar_one()
    p["c"] = cid
    uid = conn.execute(text("SELECT customer_unique_id FROM oltp.customers WHERE customer_id = :c"), p).scalar_one()
    p["u"] = uid
    out = [f"Đơn được theo dõi: `order_id = {ORDER_ID}`; `customer_id = {cid}` (mã sinh riêng cho đơn này); khách thật `customer_unique_id = {uid}`.\n"]
    out.append("#### Lớp 1 – Nguồn bán hàng `oltp` (nguyên bản, chưa làm sạch)\n")
    out.append(sec("oltp.orders", table(conn, "SELECT * FROM oltp.orders WHERE order_id = :o", p)))
    out.append(sec("oltp.customers", table(conn, "SELECT * FROM oltp.customers WHERE customer_id = :c", p)))
    out.append(sec("oltp.order_items (3 dòng hàng)", table(conn, "SELECT order_item_id, product_id, seller_id, shipping_limit_date, price, freight_value FROM oltp.order_items WHERE order_id = :o ORDER BY 1", p)))
    out.append(sec("oltp.order_payments", table(conn, "SELECT * FROM oltp.order_payments WHERE order_id = :o", p, vertical=False)))
    out.append(sec("oltp.order_reviews", table(conn, "SELECT review_id, review_score, review_comment_title, review_comment_message, review_creation_date, review_answer_timestamp FROM oltp.order_reviews WHERE order_id = :o", p)))
    out.append("Khách này còn một đơn khác ở nơi ở mới (khác mã bưu chính), nên kho tạo hai phiên bản địa chỉ cho cùng một người:\n")
    out.append(sec("oltp.customers của khách thật này (mỗi đơn một `customer_id`)", table(conn, "SELECT c.customer_id, c.customer_zip_code_prefix, c.customer_city, c.customer_state, o.order_purchase_timestamp FROM oltp.customers c JOIN oltp.orders o USING (customer_id) WHERE c.customer_unique_id = :u ORDER BY 5", p, vertical=False)))
    out.append("#### Lớp 2 – Staging `staging` (bản sao thô + mã lô nạp)\n")
    out.append(sec("staging.stg_orders", table(conn, "SELECT order_id, order_status, order_purchase_timestamp, load_batch_id, loaded_at FROM staging.stg_orders WHERE order_id = :o", p)))
    out.append("#### Lớp 3 – ODS `ods` (đã làm sạch, chuẩn hoá, có cờ chất lượng)\n")
    out.append(sec("ods.orders", table(conn, "SELECT order_id, order_status, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date, dq_flags, dq_flag_count, etl_batch_id FROM ods.orders WHERE order_id = :o", p)))
    out.append(sec("ods.customers (zip thành `char(5)`, thành phố bỏ dấu và chữ thường)", table(conn, "SELECT * FROM ods.customers WHERE customer_id = :c", p)))
    out.append(sec("ods.customer_map", table(conn, "SELECT * FROM ods.customer_map WHERE customer_id = :c", p)))
    out.append(sec("ods.order_payments (có cờ lỗi)", table(conn, "SELECT order_id, payment_sequential, payment_type, payment_installments, payment_value, dq_flags FROM ods.order_payments WHERE order_id = :o", p, vertical=False)))
    out.append("#### Lớp 4 – Kho `dw`: bảng chiều\n")
    out.append(sec("dw.dim_customer – hai phiên bản địa chỉ của khách (SCD2); đơn này thuộc phiên bản 1", table(conn, "SELECT customer_key, customer_unique_id, zip_code_prefix, city, state_code, geography_key, effective_from, effective_to, is_current, version_no FROM dw.dim_customer WHERE customer_unique_id = :u ORDER BY version_no", p, vertical=False)))
    out.append(sec("dw.dim_geography (zip của phiên bản 1)", table(conn, "SELECT g.* FROM dw.dim_geography g JOIN dw.dim_customer c USING (geography_key) WHERE c.customer_unique_id = :u AND c.version_no = 1", p)))
    out.append(sec("dw.dim_seller, dim_product của dòng hàng đầu tiên", table(conn, "SELECT s.seller_key, s.seller_id, s.city, s.state_code, s.is_from_funnel, s.acquisition_channel, s.first_sale_date, p.product_key, p.category_name_en, p.category_group, p.size_class "
                                                                                 "FROM dw.fact_order_item f JOIN dw.dim_seller s USING (seller_key) JOIN dw.dim_product p USING (product_key) WHERE f.order_id = :o AND f.order_item_id = 1", p)))
    out.append(sec("dw.dim_date (ngày mua) và dim_order_status", table(conn, "SELECT d.date_key, d.full_date, d.day_name, d.year_month, d.year_quarter, d.is_weekend, d.is_holiday_br, s.order_status, s.status_group "
                                                                         "FROM dw.fact_order_fulfillment f JOIN dw.dim_date d ON d.date_key = f.purchase_date_key JOIN dw.dim_order_status s USING (order_status_key) WHERE f.order_id = :o", p)))
    out.append("#### Lớp 4 – Kho `dw`: bảng fact\n")
    out.append(sec("dw.fact_order_fulfillment (accumulating snapshot, 1 dòng cho cả đơn)", table(conn, "SELECT * FROM dw.fact_order_fulfillment WHERE order_id = :o", p)))
    out.append(sec("dw.fact_order_item (3 dòng, khoá số nguyên thay cho mã chữ)", table(conn, "SELECT order_item_id, purchase_date_key, shipping_limit_date_key, customer_key, customer_geography_key, seller_geography_key, seller_key, product_key, order_status_key, price, freight_value, item_total FROM dw.fact_order_item WHERE order_id = :o ORDER BY 1", p, vertical=False)))
    out.append(sec("dw.fact_payment và dw.fact_review", table(conn, "SELECT 'payment' AS fact, payment_sequential::text AS k, payment_type_key::text AS a, payment_installments::text AS b, payment_value::text AS c FROM dw.fact_payment WHERE order_id = :o "
                                                                  "UNION ALL SELECT 'review', review_score::text, is_negative::text, delivered_late::text, response_hours::text FROM dw.fact_review WHERE order_id = :o", p, vertical=False)))
    out.append("#### Lớp 5 – Data mart\n")
    out.append(sec("mart_fulfillment.v_fulfillment_order (1 dòng cho đơn; đã ghép tên bang, ngày dạng date, nhóm trễ)", table(conn, "SELECT order_id, purchase_date, status_group, customer_region, customer_state, approved_date, carrier_date, delivered_date, estimated_date, lead_days, promised_days, delay_days, delay_bucket FROM mart_fulfillment.v_fulfillment_order WHERE order_id = :o", p)))
    out.append(sec("mart_fulfillment.v_shipping_distance (khoảng cách seller → khách cho từng dòng hàng)", table(conn, "SELECT order_item_id, seller_state, customer_state, round(distance_km::numeric, 1) AS distance_km, distance_band, price, freight_value, freight_ratio FROM mart_fulfillment.v_shipping_distance WHERE order_id = :o ORDER BY 1", p, vertical=False)))
    out.append(sec("Đơn này góp vào dòng của ngày mua trong mart_sales.v_sales_daily", table(conn, "SELECT d.* FROM mart_sales.v_sales_daily d JOIN dw.fact_order_fulfillment f ON f.purchase_date_key = d.date_key WHERE f.order_id = :o", p)))
    return "\n".join(out)


def mql_block(conn) -> tuple[str, str]:
    mql = conn.execute(text("SELECT f.mql_id FROM dw.fact_lead_funnel f JOIN mart_acquisition.v_seller_scorecard sc USING (seller_key) WHERE f.has_first_sale = 1 AND f.days_to_close IS NOT NULL "
                            "AND f.days_won_to_first_sale BETWEEN 25 AND 60 AND sc.orders BETWEEN 30 AND 120 ORDER BY f.mql_id LIMIT 1")).scalar_one()
    p = {"m": mql}
    seller = conn.execute(text("SELECT seller_id FROM crm.closed_deals WHERE mql_id = :m"), p).scalar_one()
    p["s"] = seller
    out = [f"MQL được theo dõi: `mql_id = {mql}`; sau khi chốt thành seller `seller_id = {seller}`.\n"]
    out.append("#### Lớp 1 – Nguồn marketing `crm`\n")
    out.append(sec("crm.mql", table(conn, "SELECT * FROM crm.mql WHERE mql_id = :m", p)))
    out.append(sec("crm.closed_deals (deal đã chốt; đây là 1 dòng với nhiều cột có thể trống)", table(conn, "SELECT * FROM crm.closed_deals WHERE mql_id = :m", p)))
    out.append("#### Lớp 2–3 – Staging và ODS\n")
    out.append(sec("staging.stg_mql / ods.mql (`origin` rỗng sẽ thành `unknown`; ở MQL này đã có giá trị)", table(conn, "SELECT m.mql_id, m.origin AS origin_goc, o.origin AS origin_ods, s.load_batch_id AS stg_batch, o.etl_batch_id AS ods_batch FROM crm.mql m JOIN staging.stg_mql s USING (mql_id) JOIN ods.mql o USING (mql_id) WHERE m.mql_id = :m", p)))
    out.append(sec("ods.closed_deals (`has_company`, `has_gtin` đổi từ boolean sang chữ; cột trống → `unknown`; cờ `dq_flags`)", table(conn, "SELECT * FROM ods.closed_deals WHERE mql_id = :m", p)))
    out.append("#### Lớp 4 – Kho `dw`\n")
    out.append(sec("dw.dim_seller – seller nối hai quy trình: bán hàng và funnel (chiều dùng chung)", table(conn, "SELECT seller_key, seller_id, city, state_code, is_from_funnel, mql_id, acquisition_origin, acquisition_channel, business_segment, lead_type, business_type, won_date, first_sale_date FROM dw.dim_seller WHERE seller_id = :s", p)))
    out.append(sec("dw.dim_lead_origin, dim_lead_profile (junk dimension) và dim_sales_rep của MQL", table(conn, "SELECT lo.origin, lo.channel_group, lp.lead_profile_key, lp.business_segment, lp.lead_behaviour_profile, lp.has_company, lp.has_gtin, lp.average_stock, sdr.rep_id AS sdr_id, sr.rep_id AS sr_id "
                                                                                   "FROM dw.fact_lead_funnel f JOIN dw.dim_lead_origin lo USING (lead_origin_key) JOIN dw.dim_lead_profile lp USING (lead_profile_key) JOIN dw.dim_sales_rep sdr ON sdr.sales_rep_key = f.sdr_key JOIN dw.dim_sales_rep sr ON sr.sales_rep_key = f.sr_key WHERE f.mql_id = :m", p)))
    out.append(sec("dw.fact_lead_funnel (accumulating snapshot: 3 mốc ngày + các khoảng thời gian)", table(conn, "SELECT f.mql_id, f.first_contact_date_key, f.won_date_key, f.first_sale_date_key, f.seller_key, f.is_won, f.has_first_sale, f.days_to_close, f.days_won_to_first_sale, f.declared_product_catalog_size, f.declared_monthly_revenue, f.seller_gmv_first_90d FROM dw.fact_lead_funnel f WHERE f.mql_id = :m", p)))
    out.append(sec("dw.fact_seller_monthly – 4 tháng đầu có đơn của seller (periodic snapshot)", table(conn, "SELECT d.year_month, f.orders, f.items, f.gmv, f.late_orders, f.avg_review_score, f.is_active, f.months_since_first_sale FROM dw.fact_seller_monthly f JOIN dw.dim_date d ON d.date_key = f.month_date_key JOIN dw.dim_seller s USING (seller_key) WHERE s.seller_id = :s ORDER BY f.month_date_key LIMIT 4", p, vertical=False)))
    out.append("#### Lớp 5 – Data mart\n")
    out.append(sec("mart_acquisition.v_seller_scorecard (1 dòng tổng hợp cho seller)", table(conn, "SELECT seller_id, acquisition_channel, acquisition_origin, first_sale_date, active_months, orders, gmv, late_rate_pct, avg_review_score, gmv_rank, cum_share_pct, abc_class, small_sample FROM mart_acquisition.v_seller_scorecard WHERE seller_id = :s", p)))
    out.append(sec("mart_acquisition.v_funnel_by_origin_month – dòng của tháng liên hệ đầu và origin của MQL", table(conn, "SELECT v.* FROM mart_acquisition.v_funnel_by_origin_month v JOIN crm.mql m ON m.origin = v.origin AND to_char(m.first_contact_date, 'YYYY-MM') = v.first_contact_month WHERE m.mql_id = :m", p)))
    return mql, "\n".join(out)


def inject(path: Path, tag: str, body: str) -> None:
    s = path.read_text(encoding="utf-8")
    a, b = f"<!-- {tag}:START -->", f"<!-- {tag}:END -->"
    i, j = s.index(a) + len(a), s.index(b)
    path.write_text(s[:i] + "\n" + body + "\n" + s[j:], encoding="utf-8")


def main() -> None:
    target = ROOT / "huong-dan" / "01-pipeline-bang-loi.md"
    with get_engine(config.DB_NAME).connect() as conn:
        inject(target, "TRACE_ORDER", order_block(conn))
        mql, blk = mql_block(conn)
        inject(target, "TRACE_MQL", blk)
    print("written", target.relative_to(ROOT), "| mql", mql)


if __name__ == "__main__":
    main()
