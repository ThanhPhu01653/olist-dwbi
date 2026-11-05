"""P1 step 2: count every known data defect (DW_DESIGN 2.3) -> handoff/data-quality.md + figure.

Zip codes were already verified in P0 (all clean), so they are only restated here; the focus is the other defects.
"""
from __future__ import annotations

from common import *  # noqa: F401,F403

BBOX = "geolocation_lat BETWEEN -33.75 AND 5.27 AND geolocation_lng BETWEEN -73.99 AND -34.79"
NORM = "lower(unaccent(trim({c})))"

CHECKS: list[dict] = []


def chk(group: str, table: str, defect: str, num_sql: str, den_sql: str, handling: str, unit: str = "dòng") -> None:
    num, den = int(scalar(num_sql)), int(scalar(den_sql))
    CHECKS.append({"group": group, "table": table, "defect": defect, "n": num, "den": den,
                   "pct": 100 * num / den if den else 0.0, "handling": handling, "unit": unit})


def cnt(table: str, where: str = "TRUE") -> str:
    return f"SELECT count(*) FROM {table} WHERE {where}"


def run_checks() -> None:
    # ---- zip (restated from P0: expected 0 everywhere) ----
    for t, c in [("oltp.customers", "customer_zip_code_prefix"), ("oltp.sellers", "seller_zip_code_prefix"),
                 ("oltp.geolocation", "geolocation_zip_code_prefix")]:
        chk("Mã bưu chính", t, "Zip không đủ 5 chữ số (mất số 0 đầu) – đã kiểm ở P0", cnt(t, f"{c} !~ '^[0-9]{{5}}$'"), cnt(t),
            "Không có lỗi ở bản CSV này; ODS vẫn chuẩn hoá char(5) bằng lpad để phòng thủ")

    # ---- geolocation ----
    g = "oltp.geolocation"
    chk("Địa lý", g, "Toạ độ nằm ngoài bounding box Brazil", cnt(g, f"NOT ({BBOX})"), cnt(g),
        "ODS lọc bỏ khỏi phép tính median (không xoá khỏi nguồn)")
    chk("Địa lý", g, "Zip có nhiều hơn 1 toạ độ khác nhau",
        f"SELECT count(*) FROM (SELECT 1 FROM {g} GROUP BY geolocation_zip_code_prefix HAVING count(DISTINCT (geolocation_lat, geolocation_lng)) > 1) x",
        f"SELECT count(DISTINCT geolocation_zip_code_prefix) FROM {g}",
        "Gom theo zip, lấy median lat/lng (ods.geolocation_zip: 1 dòng / zip)", "zip")
    chk("Địa lý", g, "Zip gắn với nhiều hơn 1 bang",
        f"SELECT count(*) FROM (SELECT 1 FROM {g} GROUP BY geolocation_zip_code_prefix HAVING count(DISTINCT geolocation_state) > 1) x",
        f"SELECT count(DISTINCT geolocation_zip_code_prefix) FROM {g}",
        "Lấy mode (bang phổ biến nhất) của zip", "zip")
    chk("Địa lý", g, "Tên thành phố lệch dấu / hoa thường / khoảng trắng",
        cnt(g, f"geolocation_city <> {NORM.format(c='geolocation_city')}"), cnt(g),
        "Chuẩn hoá lower(unaccent(trim(city))) rồi mới lấy mode")
    chk("Địa lý", g, "Tên thành phố chứa ký tự lạ sau chuẩn hoá (số, dấu *, dấu chấm…)",
        cnt(g, f"{NORM.format(c='geolocation_city')} ~ '[^a-z -]'"), cnt(g),
        "Giữ nguyên, chỉ tính mode; city của zip ưu tiên giá trị phổ biến nhất (thường là tên đúng)")
    chk("Địa lý", g, "Dòng trùng hoàn toàn (cả 5 cột giống nhau)",
        f"SELECT count(*) - count(DISTINCT (geolocation_zip_code_prefix, geolocation_lat, geolocation_lng, geolocation_city, geolocation_state)) FROM {g}",
        cnt(g), "Bị gom khi lấy median/mode theo zip")

    # ---- customers / sellers ----
    chk("Địa lý", "oltp.customers", "Tên thành phố lệch dấu / hoa thường",
        cnt("oltp.customers", f"customer_city <> {NORM.format(c='customer_city')}"), cnt("oltp.customers"),
        "Chuẩn hoá như trên (nguồn customers đã sạch)")
    chk("Địa lý", "oltp.sellers", "Tên thành phố lệch dấu / hoa thường",
        cnt("oltp.sellers", f"seller_city <> {NORM.format(c='seller_city')}"), cnt("oltp.sellers"),
        "Chuẩn hoá như trên")
    chk("Địa lý", "oltp.customers", "Zip không có trong geolocation",
        "SELECT count(*) FROM oltp.customers c WHERE NOT EXISTS (SELECT 1 FROM oltp.geolocation g WHERE g.geolocation_zip_code_prefix = c.customer_zip_code_prefix)",
        cnt("oltp.customers"), "Vẫn tạo dòng dim_geography từ city/state của customer, lat/lng = NULL (xem design-questions.md câu e)")
    chk("Địa lý", "oltp.sellers", "Zip không có trong geolocation",
        "SELECT count(*) FROM oltp.sellers s WHERE NOT EXISTS (SELECT 1 FROM oltp.geolocation g WHERE g.geolocation_zip_code_prefix = s.seller_zip_code_prefix)",
        cnt("oltp.sellers"), "Như trên")
    chk("Địa lý", "oltp.customers", "Bang của khách khác mọi bang xuất hiện trong geolocation của cùng zip",
        "SELECT count(*) FROM oltp.customers c WHERE EXISTS (SELECT 1 FROM oltp.geolocation g WHERE g.geolocation_zip_code_prefix = c.customer_zip_code_prefix) "
        "AND NOT EXISTS (SELECT 1 FROM oltp.geolocation g WHERE g.geolocation_zip_code_prefix = c.customer_zip_code_prefix AND g.geolocation_state = c.customer_state)",
        cnt("oltp.customers"), "Ghi nhận; dim_geography lấy bang theo geolocation (mode), bảng customer giữ bang gốc")

    # ---- products ----
    p = "oltp.products"
    chk("Sản phẩm", p, "Cột sai chính tả *_lenght (product_name_lenght, product_description_lenght)", "SELECT 2", "SELECT 2",
        "Đổi tên thành *_length ở ODS", "cột")
    chk("Sản phẩm", p, "Danh mục rỗng", cnt(p, "product_category_name IS NULL"), cnt(p), "Gán 'unknown'")
    chk("Sản phẩm", p, "Thiếu cân nặng hoặc kích thước", cnt(p, "product_weight_g IS NULL OR product_length_cm IS NULL OR product_height_cm IS NULL OR product_width_cm IS NULL"),
        cnt(p), "Giữ NULL + cờ dq_missing_dimensions; size_class = Unknown")
    chk("Sản phẩm", p, "Cân nặng bằng 0 g (không hợp lý về vật lý)", cnt(p, "product_weight_g = 0"), cnt(p),
        "Coi như thiếu: giữ nguyên giá trị, gắn cờ; size_class = Unknown")
    chk("Sản phẩm", p, "Danh mục có trong sản phẩm nhưng không có bản dịch (số danh mục khác nhau)",
        "SELECT count(DISTINCT product_category_name) FROM oltp.products p WHERE product_category_name IS NOT NULL AND NOT EXISTS "
        "(SELECT 1 FROM oltp.product_category_name_translation t WHERE t.product_category_name = p.product_category_name)",
        "SELECT count(DISTINCT product_category_name) FROM oltp.products", "Bổ sung thủ công qua seeds/category_translation_extra.csv", "danh mục")
    chk("Sản phẩm", p, "Sản phẩm thuộc danh mục không có bản dịch",
        "SELECT count(*) FROM oltp.products p WHERE product_category_name IS NOT NULL AND NOT EXISTS "
        "(SELECT 1 FROM oltp.product_category_name_translation t WHERE t.product_category_name = p.product_category_name)",
        cnt(p), "Như trên")

    # ---- orders ----
    o = "oltp.orders"
    chk("Đơn hàng", o, "Trạng thái delivered nhưng không có ngày giao cho khách",
        cnt(o, "order_status = 'delivered' AND order_delivered_customer_date IS NULL"), cnt(o, "order_status = 'delivered'"),
        "Không xoá đơn; gắn cờ delivered_without_date; delivered_date_key = -1")
    chk("Đơn hàng", o, "Trạng thái delivered nhưng không có ngày bàn giao vận chuyển",
        cnt(o, "order_status = 'delivered' AND order_delivered_carrier_date IS NULL"), cnt(o, "order_status = 'delivered'"),
        "Gắn cờ; handling_days / transit_days = NULL")
    chk("Đơn hàng", o, "Trạng thái delivered nhưng không có ngày duyệt",
        cnt(o, "order_status = 'delivered' AND order_approved_at IS NULL"), cnt(o, "order_status = 'delivered'"),
        "Gắn cờ; approval_hours = NULL")
    chk("Đơn hàng", o, "Có ngày giao khách nhưng trạng thái không phải delivered",
        cnt(o, "order_delivered_customer_date IS NOT NULL AND order_status <> 'delivered'"), cnt(o, "order_delivered_customer_date IS NOT NULL"),
        "Giữ nguyên trạng thái nguồn, gắn cờ")
    chk("Đơn hàng", o, "Ngày duyệt trước ngày mua", cnt(o, "order_approved_at < order_purchase_timestamp"), cnt(o, "order_approved_at IS NOT NULL"),
        "Gắn cờ approved_before_purchase; approval_hours âm → NULL", "đơn")
    chk("Đơn hàng", o, "Ngày bàn giao vận chuyển trước ngày duyệt",
        cnt(o, "order_delivered_carrier_date < order_approved_at"), cnt(o, "order_delivered_carrier_date IS NOT NULL AND order_approved_at IS NOT NULL"),
        "Gắn cờ carrier_before_approved; handling_days âm → NULL", "đơn")
    chk("Đơn hàng", o, "Ngày bàn giao vận chuyển trước ngày mua",
        cnt(o, "order_delivered_carrier_date < order_purchase_timestamp"), cnt(o, "order_delivered_carrier_date IS NOT NULL"),
        "Gắn cờ; khoảng thời gian âm → NULL", "đơn")
    chk("Đơn hàng", o, "Ngày giao khách trước ngày bàn giao vận chuyển",
        cnt(o, "order_delivered_customer_date < order_delivered_carrier_date"), cnt(o, "order_delivered_customer_date IS NOT NULL AND order_delivered_carrier_date IS NOT NULL"),
        "Gắn cờ delivered_before_carrier; transit_days âm → NULL", "đơn")
    chk("Đơn hàng", o, "Ngày giao khách trước ngày mua",
        cnt(o, "order_delivered_customer_date < order_purchase_timestamp"), cnt(o, "order_delivered_customer_date IS NOT NULL"),
        "Gắn cờ; lead_days âm → NULL", "đơn")
    chk("Đơn hàng", o, "Ngày giao dự kiến trước ngày mua",
        cnt(o, "order_estimated_delivery_date < order_purchase_timestamp"), cnt(o), "Gắn cờ", "đơn")
    chk("Đơn hàng", o, "Đơn không có dòng hàng nào", "SELECT count(*) FROM oltp.orders o WHERE NOT EXISTS (SELECT 1 FROM oltp.order_items i WHERE i.order_id = o.order_id)",
        cnt(o), "Giữ trong fact_order_fulfillment (item_count = 0); không có trong fact_order_item")
    chk("Đơn hàng", o, "Đơn không có dòng thanh toán nào", "SELECT count(*) FROM oltp.orders o WHERE NOT EXISTS (SELECT 1 FROM oltp.order_payments i WHERE i.order_id = o.order_id)",
        cnt(o), "Giữ; payment_total = 0")

    # ---- items / payments ----
    chk("Dòng hàng", "oltp.order_items", "Hạn giao cho vận chuyển (shipping_limit_date) trước ngày mua",
        "SELECT count(*) FROM oltp.order_items i JOIN oltp.orders o USING (order_id) WHERE i.shipping_limit_date < o.order_purchase_timestamp",
        cnt("oltp.order_items"), "Ghi nhận; shipping_limit_date_key vẫn nạp")
    pm = "oltp.order_payments"
    chk("Thanh toán", pm, "payment_type = not_defined", cnt(pm, "payment_type = 'not_defined'"), cnt(pm), "Giữ loại not_defined (dim_payment_type có dòng riêng)")
    chk("Thanh toán", pm, "payment_installments = 0", cnt(pm, "payment_installments = 0"), cnt(pm), "Đổi thành 1 + cờ")
    chk("Thanh toán", pm, "payment_value = 0", cnt(pm, "payment_value = 0"), cnt(pm), "Giữ nguyên; ghi nhận")
    chk("Thanh toán", pm, "Tổng thanh toán lệch tổng (price + freight) của đơn quá 1 BRL",
        "WITH it AS (SELECT order_id, sum(price + freight_value) v FROM oltp.order_items GROUP BY 1), "
        "pa AS (SELECT order_id, sum(payment_value) v FROM oltp.order_payments GROUP BY 1) "
        "SELECT count(*) FROM it JOIN pa USING (order_id) WHERE abs(it.v - pa.v) > 1",
        "SELECT count(DISTINCT i.order_id) FROM oltp.order_items i JOIN oltp.order_payments p USING (order_id)",
        "Không sửa; fact_payment giữ số tiền theo từng lần thanh toán, KPI doanh thu lấy từ price", "đơn")

    # ---- reviews ----
    r = "oltp.order_reviews"
    chk("Đánh giá", r, "review_id xuất hiện ở nhiều hơn 1 dòng (số dòng thừa)",
        f"SELECT count(*) - count(DISTINCT review_id) FROM {r}", cnt(r),
        "Khử trùng trên cặp (review_id, order_id), giữ bản có review_answer_timestamp mới nhất")
    chk("Đánh giá", r, "Số review_id bị lặp (số mã khác nhau)",
        f"SELECT count(*) FROM (SELECT 1 FROM {r} GROUP BY review_id HAVING count(*) > 1) x", f"SELECT count(DISTINCT review_id) FROM {r}",
        "Như trên", "mã")
    chk("Đánh giá", r, "Cặp (review_id, order_id) trùng", f"SELECT count(*) - count(DISTINCT (review_id, order_id)) FROM {r}", cnt(r),
        "Khử trùng (không có ở bản CSV này, PK ghép của oltp đã đảm bảo)")
    chk("Đánh giá", r, "Đơn có nhiều hơn 1 đánh giá", f"SELECT count(*) FROM (SELECT 1 FROM {r} GROUP BY order_id HAVING count(*) > 1) x",
        f"SELECT count(DISTINCT order_id) FROM {r}", "Giữ cả hai (grain fact_review = cặp review_id, order_id)", "đơn")
    chk("Đánh giá", r, "Thời điểm trả lời trước thời điểm tạo review", cnt(r, "review_answer_timestamp < review_creation_date"), cnt(r),
        "response_hours âm → NULL")
    chk("Đánh giá", r, "Ngày tạo review trước ngày mua đơn",
        f"SELECT count(*) FROM {r} v JOIN oltp.orders o USING (order_id) WHERE v.review_creation_date < o.order_purchase_timestamp", cnt(r), "Ghi nhận")
    chk("Đánh giá", r, "Không có tiêu đề comment", cnt(r, "review_comment_title IS NULL"), cnt(r), "Giữ NULL; has_comment_title = 0")
    chk("Đánh giá", r, "Không có nội dung comment", cnt(r, "review_comment_message IS NULL"), cnt(r), "Giữ NULL; has_comment_message = 0")

    # ---- funnel ----
    chk("Funnel", "crm.mql", "origin rỗng", cnt("crm.mql", "origin IS NULL"), cnt("crm.mql"), "→ 'unknown'")
    cd = "crm.closed_deals"
    for col in ["business_segment", "lead_type", "lead_behaviour_profile", "business_type", "has_company", "has_gtin", "average_stock",
                "declared_product_catalog_size"]:
        chk("Funnel", cd, f"{col} rỗng", cnt(cd, f"{col} IS NULL"), cnt(cd), "Cột phân loại → 'unknown'" if col not in ("declared_product_catalog_size",) else "Giữ NULL (non-additive)")
    chk("Funnel", cd, "declared_monthly_revenue = 0", cnt(cd, "declared_monthly_revenue = 0"), cnt(cd), "Giữ số 0, thêm cờ")
    chk("Funnel", cd, "declared_product_catalog_size = 0", cnt(cd, "declared_product_catalog_size = 0"), cnt(cd), "Giữ số 0, thêm cờ")
    chk("Funnel", cd, "Ngày chốt (won_date) trước ngày liên hệ đầu (first_contact_date)",
        f"SELECT count(*) FROM {cd} d JOIN crm.mql m USING (mql_id) WHERE d.won_date::date < m.first_contact_date", cnt(cd),
        "days_to_close âm → NULL + cờ")
    chk("Funnel", cd, "seller_id của deal không có trong oltp.sellers",
        f"SELECT count(*) FROM {cd} d WHERE NOT EXISTS (SELECT 1 FROM oltp.sellers s WHERE s.seller_id = d.seller_id)", cnt(cd),
        "Vẫn tạo dòng dim_seller (địa chỉ Unknown); đây là đặc điểm của 2 hệ thống nguồn, không phải lỗi", "deal")


def detail_sections() -> list[str]:
    lines: list[str] = []
    # coordinates per zip
    c = q("""WITH z AS (SELECT geolocation_zip_code_prefix zip, count(*) n, count(DISTINCT (geolocation_lat, geolocation_lng)) d FROM oltp.geolocation GROUP BY 1)
             SELECT count(*) zips, avg(n) avg_rows, max(n) max_rows, avg(d) avg_d, percentile_cont(0.5) WITHIN GROUP (ORDER BY d) med_d,
                    percentile_cont(0.95) WITHIN GROUP (ORDER BY d) p95_d, max(d) max_d, count(*) FILTER (WHERE d = 1) one FROM z""").iloc[0]
    lines += ["## Chi tiết: nhiều toạ độ cho một zip", "",
              f"{n(int(c.zips))} zip trong geolocation; trung bình {n(c.avg_rows, 1)} dòng/zip (tối đa {n(int(c.max_rows))}). "
              f"Chỉ {n(int(c.one))} zip ({pct(100 * c.one / c.zips)}) có đúng 1 toạ độ. Số toạ độ khác nhau mỗi zip: trung vị {n(c.med_d, 0)}, "
              f"phân vị 95 là {n(c.p95_d, 0)}, lớn nhất {n(int(c.max_d))}. Vì vậy dim_geography phải gom về **1 điểm / zip** (median lat/lng).", ""]
    # city variants
    cn = q(f"""SELECT count(DISTINCT geolocation_city) raw, count(DISTINCT {NORM.format(c='geolocation_city')}) norm FROM oltp.geolocation""").iloc[0]
    ex = q(f"""SELECT {NORM.format(c='geolocation_city')} AS chuan_hoa, geolocation_state AS bang, string_agg(DISTINCT geolocation_city, ' | ' ORDER BY geolocation_city) AS cac_cach_viet,
                      count(DISTINCT geolocation_city) k
               FROM oltp.geolocation GROUP BY 1, 2 HAVING count(DISTINCT geolocation_city) > 1 ORDER BY k DESC, 1 LIMIT 8""")
    ex_raw = q(f"""SELECT geolocation_city AS ten_goc, {NORM.format(c='geolocation_city')} AS sau_chuan_hoa, count(*) AS so_dong
                   FROM oltp.geolocation WHERE geolocation_city <> {NORM.format(c='geolocation_city')} GROUP BY 1, 2 ORDER BY 3 DESC LIMIT 6""")
    lines += ["## Chi tiết: tên thành phố lệch dấu", "",
              f"geolocation có {n(int(cn.raw))} cách viết tên thành phố; sau khi chuẩn hoá `lower(unaccent(trim()))` còn {n(int(cn.norm))} "
              f"(gộp được {n(int(cn.raw - cn.norm))} biến thể). Ví dụ tên có dấu bị chuẩn hoá:", "",
              md_table(ex_raw.assign(so_dong=ex_raw.so_dong.map(n)), ["so_dong"]), "",
              "Ví dụ một thành phố có nhiều cách viết trong cùng bang:", "",
              md_table(ex[["chuan_hoa", "bang", "cac_cach_viet"]]), ""]
    # timeline examples
    t = q("""SELECT 'duyệt trước mua' AS loi, order_id, order_purchase_timestamp AS mua, order_approved_at AS duyet,
                    order_delivered_carrier_date AS ban_giao, order_delivered_customer_date AS giao
             FROM (SELECT * FROM oltp.orders WHERE order_approved_at < order_purchase_timestamp ORDER BY order_id LIMIT 2) a
             UNION ALL
             SELECT 'bàn giao trước duyệt', order_id, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date
             FROM (SELECT * FROM oltp.orders WHERE order_delivered_carrier_date < order_approved_at ORDER BY order_id LIMIT 2) b
             UNION ALL
             SELECT 'giao trước bàn giao', order_id, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date
             FROM (SELECT * FROM oltp.orders WHERE order_delivered_customer_date < order_delivered_carrier_date ORDER BY order_id LIMIT 2) c
             UNION ALL
             SELECT 'delivered thiếu ngày giao', order_id, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date
             FROM (SELECT * FROM oltp.orders WHERE order_status = 'delivered' AND order_delivered_customer_date IS NULL ORDER BY order_id LIMIT 2) d""")
    t["order_id"] = t.order_id.str[:8] + "…"
    lines += ["## Chi tiết: ví dụ mốc thời gian sai thứ tự", "", md_table(t.astype(str).replace({"NaT": "(trống)"})), ""]
    # not_defined / installments 0 / origin
    pt = q("SELECT payment_type, count(*) c, round(100.0*count(*)/sum(count(*)) over(),2) p FROM oltp.order_payments GROUP BY 1 ORDER BY 2 DESC")
    lines += ["## Chi tiết: cơ cấu loại thanh toán", "",
              md_table(pd.DataFrame({"Loại": pt.payment_type, "Số lần": pt.c.map(n), "%": pt.p.map(lambda v: pct(float(v), 2))}), ["Số lần", "%"]), ""]
    return lines


def chart() -> str:
    df = pd.DataFrame(CHECKS)
    df = df[(df.n > 0) & (df.unit != "cột") & (df.pct < 90)].copy()
    # not errors: optional comments, and the cross-system seller gap (a property of two separate systems)
    df = df[~df.defect.str.contains("comment|seller_id của deal")]
    df["label"] = df.table.str.split(".").str[1] + ": " + df.defect.str.replace(r" \(.*?\)", "", regex=True)
    df["label"] = df.label.map(lambda s: s if len(s) <= 78 else s[:75] + "…")
    df = df.sort_values("pct", ascending=True).tail(22)
    fig, ax = plt.subplots(figsize=(13, 0.42 * len(df) + 1.8))
    bars = ax.barh(df.label, df.pct, color=BLUE, height=0.62)
    for b, (num, den, pc) in zip(bars, zip(df.n, df.den, df.pct)):
        ax.annotate(f"{pct(pc, 2 if pc < 1 else 1)} ({n(int(num))} / {n(int(den))})", (b.get_width(), b.get_y() + b.get_height() / 2),
                    xytext=(4, 0), textcoords="offset points", va="center", fontsize=8, color=INK2)
    ax.set_xscale("symlog", linthresh=1)
    ax.set_xlim(0, 160)
    ax.set_xticks([0, 1, 10, 100], ["0%", "1%", "10%", "100%"])
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("% số dòng của bảng bị ảnh hưởng (trục log mở rộng để thấy cả lỗi hiếm)")
    ax.set_title("Các lỗi dữ liệu nguồn đo được (chỉ lỗi có ít nhất 1 dòng)")
    return save(fig, "3-3-1_data_quality")


def main() -> None:
    run_checks()
    fig = chart()
    df = pd.DataFrame(CHECKS)
    out = pd.DataFrame({
        "Bảng": df.table, "Lỗi": df.defect,
        "Số lượng": [f"{n(a)} {u}" for a, u in zip(df.n, df.unit)],
        "Trên tổng": [n(d) if u != "cột" else "–" for d, u in zip(df.den, df.unit)],
        "%": ["–" if u == "cột" else pct(v, 2 if 0 < v < 1 else 1) for v, u in zip(df.pct, df.unit)],
        "Cách xử lý": df.handling,
    })
    lines = ["# Chất lượng dữ liệu nguồn – đếm từng lỗi trong DW_DESIGN §2.3 (olist_full)", "", source_note("data_quality.py"), "",
             "Mỗi dòng: lỗi, số lượng đo được bằng truy vấn, tỷ lệ trên tổng các dòng có thể bị lỗi đó, và cách xử lý ở tầng ODS/DW. "
             "Số lượng = 0 nghĩa là đã kiểm tra và không có lỗi ở bản dữ liệu này.", "",
             f"Hình: `{fig}`.", ""]
    for g in dict.fromkeys(df.group):
        sub = out[df.group == g]
        lines += [f"## {g}", "", md_table(sub, ["Số lượng", "Trên tổng", "%"]), ""]
    lines += detail_sections()
    write_md("data-quality.md", lines)
    hit = df[(df.n > 0) & (df.unit != "cột")]
    print(f"{len(df)} checks, {len(hit)} with at least one affected row")


if __name__ == "__main__":
    main()
