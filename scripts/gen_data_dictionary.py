"""Generate huong-dan/03-tu-dien-du-lieu.md: data dictionary of every table / view in schema dw and mart_*.

    python scripts/gen_data_dictionary.py
Source: COMMENT ON (pg_description), pg_catalog / information_schema (types, keys), row counts and example values from olist_dw (final state).
Mart columns have no COMMENT of their own: the meaning comes from the dw column with the same name, or from the small MART_NOTES table below.
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sqlalchemy import text

from etl import config
from etl.db import get_engine

GRAIN = {
    "dim_date": "1 ngày", "dim_geography": "1 mã bưu chính (zip)", "dim_customer": "1 phiên bản địa chỉ của 1 khách thật (SCD2)", "dim_seller": "1 seller",
    "dim_product": "1 sản phẩm", "dim_order_status": "1 trạng thái đơn", "dim_payment_type": "1 hình thức thanh toán", "dim_lead_origin": "1 giá trị origin của MQL",
    "dim_lead_profile": "1 tổ hợp thuộc tính deal", "dim_sales_rep": "1 nhân viên + vai trò (SDR/SR)",
    "fact_order_item": "1 dòng sản phẩm trong 1 đơn", "fact_order_fulfillment": "1 đơn hàng", "fact_payment": "1 lần thanh toán", "fact_review": "1 review của 1 đơn",
    "fact_lead_funnel": "1 MQL", "fact_seller_monthly": "1 seller × 1 tháng",
}
MART_NOTES = {
    "in_window": "TRUE nếu tháng thuộc 2017-01 → 2018-08 (giai đoạn dashboard dùng)", "orders": "Số đơn (distinct order_id) trong nhóm", "items": "Số dòng sản phẩm",
    "gmv": "GMV (BRL): Σ giá hàng của đơn không thuộc nhóm Failed", "freight": "Tổng phí vận chuyển (BRL)", "aov": "Giá trị TB mỗi đơn = gmv / orders",
    "year": "Năm", "quarter": "Quý (1-4)", "year_month": "Năm-tháng, vd 2017-11", "full_date": "Ngày", "date_key": "Khoá ngày yyyymmdd",
    "freight_ratio": "Phí vận chuyển / giá hàng", "avg_item_price": "Giá TB một dòng hàng", "share_pct": "Tỷ trọng (%) trong tổng", "cum_share_pct": "Tỷ trọng luỹ kế (%) khi xếp giảm dần",
    "gmv_rank": "Hạng theo GMV (1 = cao nhất)", "abc_class": "Hạng Pareto: A = 80% GMV đầu, B = đến 95%, C = phần còn lại",
    "state_code": "Mã bang 2 ký tự", "state_name": "Tên bang", "region": "Vùng của Brazil", "customer_region": "Vùng của khách", "customer_state": "Bang của khách",
    "customer_city": "Thành phố của khách", "seller_state": "Bang của seller", "purchase_date": "Ngày mua", "approved_date": "Ngày duyệt thanh toán", "carrier_date": "Ngày bàn giao vận chuyển",
    "delivered_date": "Ngày giao khách", "estimated_date": "Ngày giao dự kiến", "delay_bucket": "Nhóm trễ giao (Giao sớm … Trễ trên 7 ngày, Chưa giao)", "delay_bucket_no": "Thứ tự nhóm trễ (để sắp xếp)",
    "delivered_orders": "Số đơn đã giao", "late_orders": "Số đơn giao trễ", "canceled_orders": "Số đơn bị hủy", "on_time_rate_pct": "Tỷ lệ đơn giao đúng hạn (%)", "cancel_rate_pct": "Tỷ lệ hủy (%)",
    "avg_lead_days": "Số ngày TB từ mua đến giao", "avg_approval_hours": "Số giờ TB từ mua đến duyệt", "avg_handling_days": "Số ngày TB từ duyệt đến bàn giao vận chuyển",
    "avg_transit_days": "Số ngày TB vận chuyển", "avg_promised_days": "Số ngày hứa giao TB", "stage_no": "Thứ tự chặng", "stage": "Tên chặng của đơn", "pct_of_placed": "% so với số đơn đã đặt",
    "reviews": "Số review", "score_sum": "Tổng điểm review", "negative_reviews": "Số review tiêu cực (điểm ≤ 2)", "avg_score": "Điểm review TB", "pct_negative": "% review tiêu cực",
    "avg_response_hours": "Số giờ TB từ tạo đến trả lời review", "payments": "Số lần thanh toán", "payment_value": "Tổng giá trị thanh toán (BRL)", "avg_installments": "Số kỳ trả góp TB",
    "value_share_pct": "Tỷ trọng giá trị trong tháng (%)", "customer_unique_id": "Mã khách thật", "first_purchase": "Ngày mua đầu tiên", "last_purchase": "Ngày mua gần nhất",
    "recency_days": "Số ngày từ lần mua gần nhất đến ngày chốt dữ liệu (R)", "frequency": "Số đơn (F)", "monetary": "Tổng tiền đã mua gồm phí vận chuyển (M)", "r_score": "Điểm R 1-5 (5 = mới nhất)",
    "f_score": "Điểm F: 1 = một đơn, 3 = hai đơn, 5 = từ ba đơn", "m_score": "Điểm M 1-5", "segment": "Phân khúc RFM", "cohort_month": "Tháng mua đầu tiên của nhóm khách (cohort)",
    "months_since": "Số tháng kể từ tháng cohort", "cohort_size": "Số khách của cohort", "customers_active": "Số khách của cohort còn mua trong tháng đó", "retention_pct": "Tỷ lệ khách còn mua (%)",
    "first_contact_month": "Tháng liên hệ đầu của MQL", "mqls": "Số MQL", "won": "Số MQL đã chốt", "won_with_sale": "Số MQL đã chốt và seller có đơn", "win_rate_pct": "Tỷ lệ chốt (%) = won / mqls",
    "won_to_sale_rate_pct": "Tỷ lệ seller đã chốt có đơn (%)", "avg_days_to_close": "Số ngày TB từ liên hệ đến chốt", "avg_days_won_to_first_sale": "Số ngày TB từ chốt đến đơn đầu",
    "seller_gmv_first_90d": "GMV của seller trong 90 ngày đầu kể từ đơn đầu tiên", "active_months": "Số tháng seller có đơn", "last_active_month": "Tháng gần nhất seller có đơn",
    "late_rate_pct": "Tỷ lệ giao trễ (%)", "avg_review_score": "Điểm review TB", "small_sample": "TRUE nếu mẫu nhỏ (seller < 10 đơn; kênh < 30 seller có đơn)",
    "sellers": "Số seller", "selling_sellers": "Số seller có đơn", "pct_selling": "% seller có đơn", "gmv_per_selling_seller": "GMV TB mỗi seller có đơn",
    "distance_km": "Khoảng cách seller → khách (km, haversine); trống nếu thiếu toạ độ", "has_distance": "TRUE nếu tính được khoảng cách", "distance_band": "Nhóm khoảng cách",
    "distance_band_no": "Thứ tự nhóm khoảng cách", "status_group": "Nhóm trạng thái đơn", "latitude": "Vĩ độ", "longitude": "Kinh độ", "zips_with_coordinates": "Số zip của bang có toạ độ",
    "dw_created_at": "Thời điểm tạo dòng trong kho (cột kỹ thuật)", "dw_updated_at": "Thời điểm cập nhật dòng gần nhất (cột kỹ thuật; trống nếu chưa từng cập nhật)",
    "customers": "Số khách thật", "customer_orders": "Số đơn phía khách", "customer_gmv": "GMV phía khách", "avg_lead_days ": "", "late_rate_pct ": "",
}


def short(v) -> str:
    if v is None:
        return ""
    s = str(v).replace("|", "/").replace("\n", " ")
    return s[:38] + ("…" if len(s) > 38 else "")


def main() -> None:
    eng = get_engine(config.DB_NAME)
    out = [f"# 03 – Từ điển dữ liệu (sinh tự động {datetime.now():%Y-%m-%d %H:%M})", "",
           "Mọi bảng trong schema `dw` (kho) và `mart_*` (data mart). Ý nghĩa lấy từ `COMMENT ON` trong database (tiếng Việt), kiểu và khoá từ `information_schema` / `pg_catalog`, "
           "số dòng và **ví dụ giá trị** lấy từ `olist_dw` ở trạng thái cuối. Chạy lại: `python scripts/gen_data_dictionary.py`. Quy ước: khoá thay thế `<tên>_key`; `-1` = dòng Unknown; "
           "cột kỹ thuật `etl_batch_id`, `dw_created_at`, `dw_updated_at` cho biết lô nạp. Cột mart không có COMMENT riêng lấy nghĩa từ cột cùng tên ở `dw` hoặc từ bảng chú thích của script.", ""]
    with eng.connect() as c:
        rels = c.execute(text("""
            SELECT n.nspname, cl.relname, cl.relkind, cl.oid, obj_description(cl.oid, 'pg_class') AS cmt
            FROM pg_class cl JOIN pg_namespace n ON n.oid = cl.relnamespace
            WHERE (n.nspname = 'dw' OR n.nspname LIKE 'mart\\_%') AND cl.relkind IN ('r', 'v', 'm')
            ORDER BY CASE WHEN n.nspname = 'dw' THEN 0 ELSE 1 END, n.nspname,
                     CASE WHEN cl.relname LIKE 'dim\\_%' THEN 0 WHEN cl.relname LIKE 'fact\\_%' THEN 1 ELSE 2 END, cl.relname""")).fetchall()
        # meaning of a column name, from dw column comments
        dw_comments: dict[str, str] = {}
        for name, cmt in c.execute(text("""SELECT a.attname, col_description(a.attrelid, a.attnum) FROM pg_attribute a JOIN pg_class cl ON cl.oid = a.attrelid JOIN pg_namespace n ON n.oid = cl.relnamespace
                                           WHERE n.nspname = 'dw' AND cl.relkind = 'r' AND a.attnum > 0 AND NOT a.attisdropped AND col_description(a.attrelid, a.attnum) IS NOT NULL""")):
            dw_comments.setdefault(name, cmt)
        toc, body = [], []
        counts = {}
        for schema, name, kind, oid, cmt in rels:
            full = f"{schema}.{name}"
            n_rows = c.execute(text(f"SELECT count(*) FROM {full}")).scalar_one()
            counts[full] = n_rows
            kind_txt = {"r": "bảng", "v": "view", "m": "materialized view"}[kind]
            cols = c.execute(text("""SELECT a.attnum, a.attname, format_type(a.atttypid, a.atttypmod), NOT a.attnotnull, col_description(a.attrelid, a.attnum)
                                     FROM pg_attribute a WHERE a.attrelid = :o AND a.attnum > 0 AND NOT a.attisdropped ORDER BY a.attnum"""), {"o": oid}).fetchall()
            pk = [r[0] for r in c.execute(text("SELECT a.attname FROM pg_index i JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY (i.indkey) WHERE i.indrelid = :o AND i.indisprimary"), {"o": oid})]
            fks = {r[0]: r[1] for r in c.execute(text("""SELECT a.attname, ref.relname FROM pg_constraint k JOIN pg_attribute a ON a.attrelid = k.conrelid AND a.attnum = ANY (k.conkey)
                                                          JOIN pg_class ref ON ref.oid = k.confrelid WHERE k.conrelid = :o AND k.contype = 'f'"""), {"o": oid})}
            sample_cols = ", ".join(f'"{r[1]}"' for r in cols)
            sample = c.execute(text(f"SELECT {sample_cols} FROM {full} OFFSET {3 if n_rows > 6 else 0} LIMIT 300")).fetchall()
            examples = {}
            for i, r in enumerate(cols):
                examples[r[1]] = next((row[i] for row in sample if row[i] is not None and str(row[i]).strip() not in ("", "unknown", "n/a")), None)
                if examples[r[1]] is None:
                    examples[r[1]] = next((row[i] for row in sample if row[i] is not None), None)
            toc.append(f"- [`{full}`](#{full.replace('.', '')}) – {kind_txt}, {n_rows:,} dòng")
            block = [f"### {full}", "", f"*{kind_txt} · **{n_rows:,} dòng***", ""]
            if name in GRAIN:
                block += [f"**Grain**: {GRAIN[name]}.", ""]
            block += [f"**Mô tả**: {cmt or '(chưa có COMMENT)'}", ""]
            if pk:
                block += [f"**Khoá chính**: {', '.join(f'`{p}`' for p in pk)}", ""]
            block += ["| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |", "| --- | --- | --- | --- | --- |"]
            for _, col, typ, nullable, ccmt in cols:
                meaning = ccmt or MART_NOTES.get(col) or dw_comments.get(col) or "(xem mô tả bảng)"
                if col in fks:
                    meaning += f" → `{fks[col]}`"
                block.append(f"| `{col}` | {typ} | {'có' if nullable else 'không'} | {meaning.replace('|', '/')} | {short(examples[col])} |")
            block.append("")
            body += block
    out += ["## Mục lục", ""] + toc + [""] + body
    target = ROOT / "huong-dan" / "03-tu-dien-du-lieu.md"
    target.write_text("\n".join(out), encoding="utf-8")
    print(f"written {target.relative_to(ROOT)}: {len(rels)} tables / views, {sum(counts.values()):,} rows in total")


if __name__ == "__main__":
    main()
