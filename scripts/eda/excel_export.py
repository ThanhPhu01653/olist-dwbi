"""P1 step 7: export a clean sample of 5,000 joined orders -> exports/eda_sample.xlsx (for Excel Data Analysis ToolPak).

Population: delivered orders that have items, payments, a review and non-negative stage durations, so every
numeric column is complete (ToolPak Correlation / Regression need no blanks). Sample is deterministic (ordered by md5(order_id)).
"""
from __future__ import annotations

from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from common import *  # noqa: F401,F403

SAMPLE_SIZE = 5000
OUT = config.ROOT / "exports" / "eda_sample.xlsx"

SQL = f"""
WITH it AS (SELECT i.order_id, count(*) AS items, sum(i.price) AS price_total, sum(i.freight_value) AS freight_total,
                   sum(p.product_weight_g) AS weight_total_g, bool_and(p.product_weight_g IS NOT NULL) AS weight_ok
            FROM oltp.order_items i JOIN oltp.products p USING (product_id) GROUP BY 1),
     pa AS (SELECT order_id, sum(payment_value) AS payment_total, max(payment_installments) AS installments_max,
                   (array_agg(payment_type ORDER BY payment_value DESC))[1] AS payment_type_main FROM oltp.order_payments GROUP BY 1),
     rv AS (SELECT order_id, round(avg(review_score), 0)::int AS review_score FROM oltp.order_reviews GROUP BY 1)
SELECT o.order_id, o.order_purchase_timestamp::date AS purchase_date, to_char(o.order_purchase_timestamp, 'YYYY-MM') AS purchase_month,
       c.customer_state, it.items, it.price_total, it.freight_total, it.weight_total_g, pa.payment_total, pa.installments_max, pa.payment_type_main,
       extract(epoch FROM (o.order_approved_at - o.order_purchase_timestamp)) / 3600.0 AS approval_hours,
       extract(epoch FROM (o.order_delivered_carrier_date - o.order_approved_at)) / 86400.0 AS handling_days,
       extract(epoch FROM (o.order_delivered_customer_date - o.order_delivered_carrier_date)) / 86400.0 AS transit_days,
       extract(epoch FROM (o.order_delivered_customer_date - o.order_purchase_timestamp)) / 86400.0 AS lead_days,
       (o.order_delivered_customer_date::date - o.order_estimated_delivery_date::date) AS delay_days,
       rv.review_score
FROM oltp.orders o JOIN oltp.customers c USING (customer_id)
JOIN it USING (order_id) JOIN pa USING (order_id) JOIN rv USING (order_id)
WHERE o.order_status = 'delivered' AND o.order_approved_at >= o.order_purchase_timestamp
  AND o.order_delivered_carrier_date >= o.order_approved_at AND o.order_delivered_customer_date >= o.order_delivered_carrier_date
  AND it.weight_ok AND it.weight_total_g > 0 AND it.price_total > 0
"""

DICTIONARY = [
    # text / date columns first (A:G), then ONE contiguous block of numeric columns (H:U) for the ToolPak
    ("order_id", "Mã đơn hàng", "text", "Khoá của đơn; không dùng cho phân tích số"),
    ("purchase_date", "Ngày mua", "ngày", ""),
    ("purchase_month", "Tháng mua (YYYY-MM)", "text", "Dùng cho PivotTable / Histogram theo tháng"),
    ("customer_state", "Bang của khách (2 ký tự)", "text", "27 bang; xem `region` để gộp vùng"),
    ("region", "Vùng của khách", "text", "Norte / Nordeste / Centro-Oeste / Sudeste / Sul"),
    ("payment_type_main", "Hình thức thanh toán chiếm tỷ trọng lớn nhất", "text", "credit_card / boleto / voucher / debit_card"),
    ("delay_group", "Nhóm trễ", "text", "Sớm / Đúng hạn / Trễ 1–3 / Trễ 4–7 / Trễ >7 ngày"),
    ("items", "Số dòng hàng trong đơn", "số", ""),
    ("price_total", "Tổng tiền hàng (price)", "BRL", "Tổng price các dòng hàng"),
    ("freight_total", "Tổng phí vận chuyển", "BRL", ""),
    ("freight_ratio", "Phí vận chuyển ÷ tiền hàng", "tỷ lệ", "freight_total / price_total"),
    ("weight_total_g", "Tổng cân nặng", "gram", "Tổng cân nặng sản phẩm"),
    ("payment_total", "Tổng số tiền khách thanh toán", "BRL", "Có thể lệch price + freight (voucher, làm tròn)"),
    ("installments_max", "Số kỳ trả góp lớn nhất", "số kỳ", "Đã đổi 0 → 1 nếu nguồn ghi 0"),
    ("approval_hours", "Giờ từ lúc mua đến lúc duyệt", "giờ", "Chặng 1"),
    ("handling_days", "Ngày từ duyệt đến bàn giao vận chuyển", "ngày", "Chặng 2"),
    ("transit_days", "Ngày từ bàn giao đến giao khách", "ngày", "Chặng 3"),
    ("lead_days", "Tổng thời gian từ mua đến giao khách", "ngày", "Bằng tổng 3 chặng"),
    ("delay_days", "Ngày giao thực tế − ngày dự kiến", "ngày", "Âm = giao sớm, 0 = đúng ngày, dương = trễ"),
    ("is_late", "Giao trễ?", "0/1", "1 nếu delay_days > 0"),
    ("review_score", "Điểm review (1–5)", "số", "Trung bình các review của đơn, làm tròn"),
]


def write_guide(df: pd.DataFrame, pool: int) -> None:
    """handoff/excel-toolpak-guide.md: step-by-step ToolPak guide + expected values computed from the same sample."""
    num = df[[c for c, *_ in DICTIONARY[7:]]]
    d = num.describe().T
    show = ["price_total", "freight_total", "lead_days", "delay_days", "review_score"]
    exp = pd.DataFrame({"Biến": show, "Mean": [n(d.loc[c, "mean"], 2) for c in show], "Median": [n(num[c].median(), 2) for c in show],
                        "Standard Deviation": [n(d.loc[c, "std"], 2) for c in show], "Min": [n(d.loc[c, "min"], 2) for c in show],
                        "Max": [n(d.loc[c, "max"], 2) for c in show], "Count": [n(int(d.loc[c, "count"])) for c in show]})
    pairs = [("delay_days", "review_score"), ("lead_days", "review_score"), ("price_total", "payment_total"), ("freight_total", "weight_total_g"), ("transit_days", "lead_days")]
    cor = pd.DataFrame({"Cặp biến": [f"{a} – {b}" for a, b in pairs], "Hệ số Pearson (Excel Correlation)": [n(num[a].corr(num[b]), 3) for a, b in pairs]})
    late = df[df.is_late == 1].review_score.mean()
    ontime = df[df.is_late == 0].review_score.mean()
    bins = list(range(0, 61, 5))
    cnt = pd.cut(df.lead_days, [-1] + bins[1:] + [np.inf]).value_counts(sort=False)
    X, y = df.delay_days.astype(float), df.review_score.astype(float)
    slope = float(np.cov(X, y)[0, 1] / X.var(ddof=1))
    r2 = float(np.corrcoef(X, y)[0, 1] ** 2)
    lines = ["# Hướng dẫn Excel Data Analysis ToolPak (cho KT3)", "", source_note("excel_export.py"), "",
             "Môn học yêu cầu đa dạng công cụ phân tích: ngoài Power BI, dùng Excel Data Analysis ToolPak cho thống kê mô tả, tương quan, histogram.", "",
             "## File dữ liệu", "",
             f"- `exports/eda_sample.xlsx`, sheet **du_lieu**: {n(len(df))} đơn đã giao (mẫu cố định từ {n(pool)} đơn đủ điều kiện), 21 cột, **không có ô trống**.",
             "- Cột A–G là chữ / ngày (order_id, purchase_date, purchase_month, customer_state, region, payment_type_main, delay_group).",
             "- **Cột H–U là 14 cột số liên tiếp** (items … review_score) để ToolPak dùng một vùng chọn duy nhất: `H1:U5001` (dòng 1 là tiêu đề).",
             "- Sheet **mo_ta_cot**: ý nghĩa, đơn vị từng cột. Sheet **thong_tin**: nguồn và cách lấy mẫu.", "",
             "## Bước 0 – Bật ToolPak (làm một lần)", "",
             "1. Excel → **File → Options → Add-ins**.", "2. Ô *Manage* chọn **Excel Add-ins** → bấm **Go…**.",
             "3. Tích **Analysis ToolPak** → **OK**. (Mac: *Tools → Excel Add-ins…* → tích Analysis ToolPak.)",
             "4. Tab **Data** xuất hiện nút **Data Analysis** ở góc phải.", "",
             "## Bước 1 – Descriptive Statistics (thống kê mô tả)", "",
             "1. Data → **Data Analysis** → **Descriptive Statistics** → OK.",
             "2. *Input Range*: `du_lieu!$H$1:$U$5001`; *Grouped By*: Columns; tích **Labels in first row**.",
             "3. *Output Range*: chọn ô trống ở sheet mới (ví dụ `thong_ke!$A$1`); tích **Summary statistics** và **Confidence Level for Mean 95%**.",
             "4. OK. Kết quả có 14 cột, mỗi cột gồm Mean, Standard Error, Median, Mode, Standard Deviation, Sample Variance, Kurtosis, Skewness, Range, Min, Max, Sum, Count.",
             "5. **Đối chiếu** (phải khớp):", "", md_table(exp, list(exp.columns[1:])), "",
             "## Bước 2 – Correlation (tương quan Pearson)", "",
             "1. Data Analysis → **Correlation** → OK.", "2. *Input Range*: `du_lieu!$H$1:$U$5001`; Columns; tích **Labels in first row**; *Output Range*: sheet mới (`tuong_quan!$A$1`).",
             "3. Được ma trận 14 × 14. Tô màu bằng *Home → Conditional Formatting → Color Scales* (xanh dương – trắng – đỏ, cố định −1…1).",
             "4. **Đối chiếu**:", "", md_table(cor, ["Hệ số Pearson (Excel Correlation)"]), "",
             "Lưu ý: Excel dùng hệ số **Pearson**, còn hình `figures/3-3-1_correlation_matrix.png` dùng **Spearman** (theo thứ hạng, hợp với dữ liệu lệch phải), nên các hệ số khác nhau. "
             "Cả hai cùng cho thấy trễ giao hàng làm điểm review giảm.", "",
             "## Bước 3 – Histogram (phân phối thời gian giao hàng)", "",
             "1. Ở sheet mới, ô `A1` gõ `Bin`, rồi `A2:A13` gõ 5, 10, 15, …, 60 (bước 5 ngày).",
             "2. Data Analysis → **Histogram** → OK. *Input Range*: `du_lieu!$R$1:$R$5001` (lead_days); *Bin Range*: `A1:A13`; tích **Labels**.",
             "3. *Output Range*: `C1`; tích **Chart Output** (và **Pareto** nếu muốn). OK.",
             "4. Đổi tên trục: X = “Lead time (ngày)”, Y = “Số đơn”; xoá khoảng cách giữa cột (Format Data Series → Gap Width = 0%).",
             "5. **Đối chiếu** số đơn theo khoảng (khoảng cuối “More” = trên 60 ngày):", "",
             md_table(pd.DataFrame({"Bin (Excel)": [str(b) for b in bins[1:]] + ["More"],
                                    "Khoảng lead_days (ngày)": [f"≤ {bins[1]}"] + [f"> {bins[i]} và ≤ {bins[i + 1]}" for i in range(1, len(bins) - 1)] + [f"> {bins[-1]}"],
                                    "Số đơn": [n(int(v)) for v in cnt.values]}), ["Số đơn"]), "",
             "## Bước 4 (tuỳ chọn) – Regression: điểm review theo số ngày trễ", "",
             "1. Data Analysis → **Regression** → OK.", "2. *Input Y Range*: `du_lieu!$U$1:$U$5001` (review_score); *Input X Range*: `du_lieu!$S$1:$S$5001` (delay_days); tích **Labels**.",
             "3. *Output Range*: sheet mới. OK.", f"4. **Đối chiếu**: hệ số dốc (X Variable 1) ≈ {n(slope, 4)} điểm review cho mỗi ngày trễ thêm; R Square ≈ {n(r2, 3)}.",
             f"5. Gợi ý nhận xét: trong mẫu, đơn giao trễ có điểm TB {n(late, 2)} so với {n(ontime, 2)} của đơn không trễ (cột `is_late`).", "",
             "## Gợi ý đưa vào báo cáo (mục 3.3.1 / công cụ phân tích)", "",
             "- Chụp ảnh bảng Descriptive Statistics, ma trận Correlation (có tô màu) và biểu đồ Histogram; đặt tên `figures/3-3-1_excel_<tên>.png`.",
             "- Nói rõ đây là **mẫu 5.000 đơn**, số liệu toàn bộ nằm ở `handoff/distributions.md` và `handoff/correlations.md`."]
    write_md("excel-toolpak-guide.md", lines)


def main() -> None:
    df = q(SQL)
    pool = len(df)
    for c in df.columns.difference(["order_id", "purchase_date", "purchase_month", "customer_state", "payment_type_main"]):
        df[c] = pd.to_numeric(df[c])
    df["_k"] = df.order_id.map(lambda s: __import__("hashlib").md5(s.encode()).hexdigest())
    df = df.sort_values("_k").head(SAMPLE_SIZE).drop(columns="_k").reset_index(drop=True)
    df["region"] = df.customer_state.map(STATE_REGION)
    df["installments_max"] = df.installments_max.clip(lower=1)  # source has 0 installments for a few payments
    df["freight_ratio"] = df.freight_total / df.price_total
    df["is_late"] = (df.delay_days > 0).astype(int)
    df["delay_group"] = np.select([df.delay_days < 0, df.delay_days == 0, df.delay_days <= 3, df.delay_days <= 7],
                                  ["Sớm", "Đúng hạn", "Trễ 1–3 ngày", "Trễ 4–7 ngày"], default="Trễ >7 ngày")
    cols = [c for c, *_ in DICTIONARY]
    df = df[cols]
    for c in ["price_total", "freight_total", "payment_total"]:
        df[c] = df[c].astype(float).round(2)
    for c in ["freight_ratio", "approval_hours", "handling_days", "transit_days", "lead_days"]:
        df[c] = df[c].astype(float).round(3)
    df["purchase_date"] = pd.to_datetime(df.purchase_date)
    assert not df.isna().any().any(), "sample must have no blanks"

    OUT.parent.mkdir(exist_ok=True)
    with pd.ExcelWriter(OUT, engine="openpyxl", datetime_format="yyyy-mm-dd") as xw:
        df.to_excel(xw, sheet_name="du_lieu", index=False)
        pd.DataFrame(DICTIONARY, columns=["Cột", "Ý nghĩa", "Đơn vị", "Ghi chú"]).to_excel(xw, sheet_name="mo_ta_cot", index=False)
        info = pd.DataFrame({"Mục": ["Nguồn", "Quần thể", "Số dòng trong mẫu", "Cách lấy mẫu", "Hết dữ liệu trống?"],
                             "Nội dung": ["olist_full (đơn đã giao, có dòng hàng, thanh toán, review)",
                                          f"{n(pool)} đơn thoả: status = delivered, các mốc thời gian đúng thứ tự, cân nặng đủ",
                                          n(len(df)), "Sắp theo md5(order_id), lấy 5.000 đầu (cố định, chạy lại cho cùng kết quả)", "Có: mọi cột đầy đủ"]})
        info.to_excel(xw, sheet_name="thong_tin", index=False)
        for ws in xw.book.worksheets:
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill("solid", fgColor="2A78D6")
                cell.alignment = Alignment(vertical="center")
            ws.freeze_panes = "A2"
            for i, col in enumerate(ws.columns, 1):
                width = max(len(str(c.value)) if c.value is not None else 0 for c in list(col)[:200])
                ws.column_dimensions[get_column_letter(i)].width = min(max(width + 2, 10), 60)
        ws = xw.book["du_lieu"]
        ws.column_dimensions["A"].width = 36
        ws.auto_filter.ref = ws.dimensions
    write_guide(df, pool)
    print(f"written: {OUT.relative_to(config.ROOT)}  ({len(df)} rows from a pool of {pool}; {OUT.stat().st_size / 1024:.0f} KB)")
    print(df.describe().T[["mean", "std", "min", "max"]].round(2).to_string())


if __name__ == "__main__":
    main()
