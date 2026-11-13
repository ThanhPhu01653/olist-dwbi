"""P8-D shared helpers: item-level and order-level data frames from olist_full, and a section writer for handoff/2026-11-14-P8-eda.md.

Each P8 EDA script owns one section (marker comments), so scripts can be re-run independently and the file keeps a fixed order.
"""
from __future__ import annotations

import re

from common import *  # noqa: F401,F403

EDA_MD = HANDOFF_DIR / "2026-11-14-P8-eda.md"
ORDER = ["outliers", "association", "seasonality", "describe", "dictionary"]
TITLES = {
    "outliers": "D1. Ngoại lai (IQR và Isolation Forest)",
    "association": "D2. Tương quan giữa biến rời rạc (Cramér's V và tỉ số tương quan η)",
    "seasonality": "D3. Khuynh hướng và mùa vụ",
    "describe": "D4. Thống kê đặc trưng",
    "dictionary": "D5. Từ điển dữ liệu nguồn",
}
HEADER = ["# P8-D – Khám phá dữ liệu bổ sung (14/11/2026)", "",
          "*Sinh tự động bởi các script `scripts/eda/p8_*.py` trên database `olist_full`; mỗi mục do một script ghi, chạy lại script để cập nhật. Mọi số liệu lấy từ truy vấn thật.*", ""]


def section(key: str, lines: list[str]) -> None:
    """Replace (or add) the section of one script in the shared handoff file, keeping the order of ORDER."""
    secs = {}
    if EDA_MD.exists():
        for k, body in re.findall(r"<!-- sec:(\w+) -->\n(.*?)<!-- /sec:\1 -->", EDA_MD.read_text(encoding="utf-8"), flags=re.S):
            secs[k] = body
    secs[key] = "## " + TITLES[key] + "\n\n" + "\n".join(lines).rstrip() + "\n"
    out = list(HEADER)
    for k in ORDER:
        if k in secs:
            out.append(f"<!-- sec:{k} -->\n{secs[k]}<!-- /sec:{k} -->\n")
    EDA_MD.write_text("\n".join(out), encoding="utf-8")
    print("written:", EDA_MD.relative_to(ROOT), f"(section {key})")


def items_df() -> pd.DataFrame:
    """One row per order line with product, seller and order context (all order statuses)."""
    return q("""
        SELECT i.order_id, i.order_item_id, i.price, i.freight_value, i.seller_id, p.product_weight_g, p.product_category_name,
               o.order_status, c.customer_state, s.seller_state,
               extract(epoch FROM (o.order_delivered_customer_date - o.order_purchase_timestamp)) / 86400.0 AS lead_days,
               (o.order_delivered_customer_date::date - o.order_estimated_delivery_date::date) AS delay_days
        FROM oltp.order_items i
        JOIN oltp.orders o USING (order_id) JOIN oltp.customers c USING (customer_id)
        JOIN oltp.sellers s ON s.seller_id = i.seller_id LEFT JOIN oltp.products p USING (product_id)""")


def orders_df() -> pd.DataFrame:
    """One row per order: status, regions, main payment type, main category group, lateness and review score."""
    df = q("""
        WITH it AS (SELECT DISTINCT ON (i.order_id) i.order_id, p.product_category_name, s.seller_state, i.price
                    FROM oltp.order_items i LEFT JOIN oltp.products p USING (product_id) JOIN oltp.sellers s USING (seller_id)
                    ORDER BY i.order_id, i.price DESC, i.order_item_id),
             pa AS (SELECT DISTINCT ON (order_id) order_id, payment_type FROM oltp.order_payments ORDER BY order_id, payment_sequential),
             rv AS (SELECT order_id, avg(review_score) AS review_score FROM oltp.order_reviews GROUP BY 1)
        SELECT o.order_id, o.order_status, c.customer_state, it.seller_state, it.product_category_name, pa.payment_type, rv.review_score,
               it.price AS main_price,
               extract(epoch FROM (o.order_delivered_customer_date - o.order_purchase_timestamp)) / 86400.0 AS lead_days,
               (o.order_delivered_customer_date::date - o.order_estimated_delivery_date::date) AS delay_days,
               o.order_purchase_timestamp
        FROM oltp.orders o JOIN oltp.customers c USING (customer_id)
        LEFT JOIN it USING (order_id) LEFT JOIN pa USING (order_id) LEFT JOIN rv USING (order_id)""")
    cg = pd.read_csv(ROOT / "seeds" / "category_group.csv")
    df = df.merge(cg, on="product_category_name", how="left")
    has_item = df["seller_state"].notna()  # orders without any order line have no seller and no product
    df["category_group"] = df["category_group"].fillna("Unknown").where(has_item)
    df["customer_region"] = df["customer_state"].map(STATE_REGION).fillna("Unknown")
    df["seller_region"] = df["seller_state"].map(STATE_REGION).where(has_item)
    df["is_late"] = np.where(df["delay_days"].notna(), (df["delay_days"] > 0).astype(float), np.nan)
    df["review_group"] = pd.cut(df["review_score"], [0, 2.5, 3.5, 5.1], labels=["tiêu cực (1-2)", "trung tính (3)", "tích cực (4-5)"])
    return df
