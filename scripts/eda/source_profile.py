"""P8-C1: source-data profile for report section 2.4 -> handoff/2026-11-14-P8-source.md + figures + report/tables.

1. Update frequency over time (orders/day and /month, order lines/month, reviews/month, MQL/month, deals/month)
   and a table: source table | average and peak volume per day | update frequency | proposed processing technology.
2. Data taxonomy: 11 source tables in 4 groups (master, transaction, interaction, reference) with one real value per column,
   plus a classification by data type, sensitivity and volatility.
Runs on olist_full. Window of "normal" activity = 2017-01-01 .. 2018-08-31 (99.6% of orders).
"""
from __future__ import annotations

from common import *  # noqa: F401,F403

import textwrap

from matplotlib.patches import FancyBboxPatch

W0, W1 = "2017-01-01", "2018-08-31"
N_DAYS = (pd.Timestamp(W1) - pd.Timestamp(W0)).days + 1
TABLES_DIR = ROOT / "report" / "tables"

# ----------------------------------------------------------------------------- 1. frequency
SERIES = {
    "orders": "SELECT order_purchase_timestamp::date AS d, count(*) AS v FROM oltp.orders GROUP BY 1",
    "items": "SELECT o.order_purchase_timestamp::date AS d, count(*) AS v FROM oltp.order_items i JOIN oltp.orders o USING (order_id) GROUP BY 1",
    "payments": "SELECT o.order_purchase_timestamp::date AS d, count(*) AS v FROM oltp.order_payments p JOIN oltp.orders o USING (order_id) GROUP BY 1",
    "reviews": "SELECT review_creation_date::date AS d, count(*) AS v FROM oltp.order_reviews GROUP BY 1",
    "mql": "SELECT first_contact_date AS d, count(*) AS v FROM crm.mql GROUP BY 1",
    "deals": "SELECT won_date::date AS d, count(*) AS v FROM crm.closed_deals GROUP BY 1",
    "customers": "SELECT d, count(*) AS v FROM (SELECT min(o.order_purchase_timestamp::date) AS d FROM oltp.customers c JOIN oltp.orders o USING (customer_id) GROUP BY c.customer_unique_id) t GROUP BY 1",
    "sellers": "SELECT d, count(*) AS v FROM (SELECT min(o.order_purchase_timestamp::date) AS d FROM oltp.order_items i JOIN oltp.orders o USING (order_id) GROUP BY i.seller_id) t GROUP BY 1",
    "products": "SELECT d, count(*) AS v FROM (SELECT min(o.order_purchase_timestamp::date) AS d FROM oltp.order_items i JOIN oltp.orders o USING (order_id) GROUP BY i.product_id) t GROUP BY 1",
}
daily = {}
for k, sql in SERIES.items():
    df = q(sql)
    df["d"] = pd.to_datetime(df["d"])
    daily[k] = df.set_index("d")["v"].sort_index()


def stats(k: str) -> tuple[float, int, str]:
    s = daily[k]
    win = s[(s.index >= W0) & (s.index <= W1)]
    return win.sum() / N_DAYS, int(win.max()), win.idxmax().strftime("%d/%m/%Y")


FREQ_ROWS = [
    # table, series key, update frequency, proposed technology
    ("oltp.orders", "orders", "liên tục: mỗi đơn đổi trạng thái 4–5 lần (mua, duyệt, bàn giao, giao)", "lô hằng ngày bằng procedure PostgreSQL; nếu cần gần thời gian thực: CDC + Kafka (chương 5)"),
    ("oltp.order_items", "items", "cùng lúc với đơn (ghi một lần khi đặt)", "lô hằng ngày, nạp theo khoá (order_id, order_item_id)"),
    ("oltp.order_payments", "payments", "cùng lúc với đơn", "lô hằng ngày; có thể gộp chung job với đơn"),
    ("oltp.order_reviews", "reviews", "sau khi giao hàng (trễ vài ngày đến hai tuần)", "lô hằng ngày; thử lại dòng mồ côi khi đơn chưa về"),
    ("oltp.customers", "customers", "khi khách mới đặt đơn đầu tiên", "lô hằng ngày; SCD2 khi đổi mã bưu chính"),
    ("oltp.sellers", "sellers", "khi seller bán đơn đầu tiên", "lô hằng ngày"),
    ("oltp.products", "products", "khi sản phẩm bán lần đầu", "lô hằng ngày"),
    ("crm.mql", "mql", "hằng ngày (khách tiềm năng để lại thông tin)", "lô hằng ngày; luồng sự kiện nếu cần phản hồi nhanh cho đội sales"),
    ("crm.closed_deals", "deals", "vài ngày một lần (khi chốt hợp đồng)", "lô hằng ngày"),
]
freq = []
for table, key, upd, tech in FREQ_ROWS:
    avg, peak, peak_day = stats(key)
    freq.append({"Bảng nguồn": table, "Trung bình / ngày": n(avg, 1), "Đỉnh một ngày": f"{n(peak)} ({peak_day})", "Tần suất cập nhật": upd, "Công nghệ xử lý đề xuất": tech})
for table, upd, tech in [("oltp.geolocation", "tĩnh (bảng tham chiếu, đổi khi có bản đồ mới)", "nạp lại toàn phần theo quý; gom về một điểm cho mỗi mã bưu chính"),
                         ("oltp.product_category_name_translation", "tĩnh (71 dòng)", "bảng seed, nạp lại khi có danh mục mới")]:
    freq.append({"Bảng nguồn": table, "Trung bình / ngày": "0", "Đỉnh một ngày": "0", "Tần suất cập nhật": upd, "Công nghệ xử lý đề xuất": tech})
freq_df = pd.DataFrame(freq)

# --- figure: 6 panels
fig, axes = plt.subplots(3, 2, figsize=(11, 9.2))
ax = axes[0, 0]
o = daily["orders"][(daily["orders"].index >= W0) & (daily["orders"].index <= W1)].asfreq("D", fill_value=0)
ax.plot(o.index, o.values, color=BLUE, lw=0.6, alpha=0.55, label="theo ngày")
ax.plot(o.index, o.rolling(7, center=True).mean(), color=ORANGE, lw=1.6, label="TB trượt 7 ngày")
pk = o.idxmax()
ax.annotate(f"Black Friday {pk:%d/%m/%Y}: {n(o.max())} đơn", (pk, o.max()), xytext=(22, -4), textcoords="offset points", fontsize=8, color=INK2,
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7))
ax.set_title("Số đơn mỗi ngày"); vn_axis(ax); ax.legend(fontsize=8, loc="upper left")


def monthly(ax, key, color, title, label_peak=True):
    s = daily[key][(daily[key].index >= "2016-09-01") & (daily[key].index <= "2018-10-31")]
    m = s.resample("MS").sum()
    bars = ax.bar(m.index, m.values, width=22, color=color)
    ax.set_title(title); vn_axis(ax)
    if label_peak:
        i = int(np.argmax(m.values))
        ax.annotate(n(m.values[i]), (m.index[i], m.values[i]), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8, color=INK2)
    ax.margins(x=0.02)


monthly(axes[0, 1], "orders", BLUE, "Số đơn mỗi tháng")
monthly(axes[1, 0], "items", AQUA, "Số dòng hàng mỗi tháng (theo ngày mua)")
monthly(axes[1, 1], "reviews", MAGENTA, "Số review mỗi tháng (theo ngày tạo review)")
monthly(axes[2, 0], "mql", VIOLET, "Số MQL mới mỗi tháng")
monthly(axes[2, 1], "deals", YELLOW, "Số deal chốt mỗi tháng")
for a in axes.ravel():
    a.tick_params(axis="x", labelrotation=30, labelsize=8)
fig.suptitle("Tần suất cập nhật của các bảng nguồn theo thời gian (olist_full)", x=0.01, ha="left", fontsize=13, fontweight="bold")
fig.tight_layout()
f_freq = save(fig, "2-4_tan_suat_cap_nhat")

# ----------------------------------------------------------------------------- 2. taxonomy
ex = lambda sql: str(q(sql).iloc[0, 0])
EXAMPLES = {
    "customers": [("customer_unique_id", "SELECT customer_unique_id FROM oltp.customers ORDER BY customer_id LIMIT 1"),
                  ("customer_city", "SELECT customer_city FROM oltp.customers ORDER BY customer_id LIMIT 1")],
    "sellers": [("seller_id", "SELECT seller_id FROM oltp.sellers ORDER BY seller_id LIMIT 1"),
                ("seller_state", "SELECT seller_state FROM oltp.sellers ORDER BY seller_id LIMIT 1")],
    "products": [("product_category_name", "SELECT product_category_name FROM oltp.products ORDER BY product_id LIMIT 1"),
                 ("product_weight_g", "SELECT product_weight_g FROM oltp.products ORDER BY product_id LIMIT 1")],
    "orders": [("order_status", "SELECT order_status FROM oltp.orders ORDER BY order_id LIMIT 1"),
               ("order_purchase_timestamp", "SELECT order_purchase_timestamp FROM oltp.orders ORDER BY order_id LIMIT 1")],
    "order_items": [("price", "SELECT price FROM oltp.order_items ORDER BY order_id, order_item_id LIMIT 1"),
                    ("freight_value", "SELECT freight_value FROM oltp.order_items ORDER BY order_id, order_item_id LIMIT 1")],
    "order_payments": [("payment_type", "SELECT payment_type FROM oltp.order_payments ORDER BY order_id, payment_sequential LIMIT 1"),
                       ("payment_installments", "SELECT payment_installments FROM oltp.order_payments ORDER BY order_id, payment_sequential LIMIT 1")],
    "order_reviews": [("review_score", "SELECT review_score FROM oltp.order_reviews ORDER BY review_id, order_id LIMIT 1"),
                      ("review_creation_date", "SELECT review_creation_date::date FROM oltp.order_reviews ORDER BY review_id, order_id LIMIT 1")],
    "mql": [("origin", "SELECT origin FROM crm.mql ORDER BY mql_id LIMIT 1"),
            ("first_contact_date", "SELECT first_contact_date FROM crm.mql ORDER BY mql_id LIMIT 1")],
    "closed_deals": [("business_segment", "SELECT business_segment FROM crm.closed_deals ORDER BY mql_id LIMIT 1"),
                     ("won_date", "SELECT won_date::date FROM crm.closed_deals ORDER BY mql_id LIMIT 1")],
    "geolocation": [("geolocation_zip_code_prefix", "SELECT geolocation_zip_code_prefix FROM oltp.geolocation ORDER BY id LIMIT 1"),
                    ("geolocation_lat", "SELECT round(geolocation_lat::numeric, 4) FROM oltp.geolocation ORDER BY id LIMIT 1")],
    "category_translation": [("product_category_name_english", "SELECT product_category_name_english FROM oltp.product_category_name_translation ORDER BY product_category_name LIMIT 1")],
}
GROUPS = [
    ("Dữ liệu chủ (master)", BLUE, ["customers", "sellers", "products"], "mô tả đối tượng, ít đổi, nhiều giao dịch tham chiếu tới"),
    ("Dữ liệu giao dịch", ORANGE, ["orders", "order_items", "order_payments"], "ghi lại sự kiện mua bán, tăng liên tục, mỗi dòng gắn một thời điểm"),
    ("Dữ liệu tương tác", MAGENTA, ["order_reviews", "mql", "closed_deals"], "phản hồi của khách và hành trình thu hút seller"),
    ("Dữ liệu tham chiếu", GREEN, ["geolocation", "category_translation"], "danh mục tra cứu, gần như tĩnh"),
]
NAME = {"customers": "customers", "sellers": "sellers", "products": "products", "orders": "orders", "order_items": "order_items",
        "order_payments": "order_payments", "order_reviews": "order_reviews", "mql": "mql", "closed_deals": "closed_deals",
        "geolocation": "geolocation", "category_translation": "category_translation"}
ROWS_CNT = {"customers": 99441, "sellers": 3095, "products": 32951, "orders": 99441, "order_items": 112650, "order_payments": 103886,
            "order_reviews": 99224, "mql": 8000, "closed_deals": 842, "geolocation": 1000163, "category_translation": 71}
real_rows = {
    "customers": scalar("SELECT count(*) FROM oltp.customers"), "sellers": scalar("SELECT count(*) FROM oltp.sellers"),
    "products": scalar("SELECT count(*) FROM oltp.products"), "orders": scalar("SELECT count(*) FROM oltp.orders"),
    "order_items": scalar("SELECT count(*) FROM oltp.order_items"), "order_payments": scalar("SELECT count(*) FROM oltp.order_payments"),
    "order_reviews": scalar("SELECT count(*) FROM oltp.order_reviews"), "mql": scalar("SELECT count(*) FROM crm.mql"),
    "closed_deals": scalar("SELECT count(*) FROM crm.closed_deals"), "geolocation": scalar("SELECT count(*) FROM oltp.geolocation"),
    "category_translation": scalar("SELECT count(*) FROM oltp.product_category_name_translation"),
}
ex_vals = {t: [(c, ex(s)) for c, s in lst] for t, lst in EXAMPLES.items()}
for t in ex_vals:
    ex_vals[t] = [(c, v if len(v) <= 22 else v[:8] + "…") for c, v in ex_vals[t]]

fig, ax = plt.subplots(figsize=(11.5, 6.6))
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off"); ax.grid(False)
ax.add_patch(FancyBboxPatch((1, 43), 13, 14, boxstyle="round,pad=0.4", fc=INK, ec=INK))
ax.text(7.5, 50, "11 bảng nguồn\n1.559.764 dòng", color="white", ha="center", va="center", fontsize=10, fontweight="bold")
ys = [86, 63, 40, 17]
for (title, col, tabs, desc), y in zip(GROUPS, ys):
    ax.add_patch(FancyBboxPatch((20, y - 8), 18, 16, boxstyle="round,pad=0.3", fc=col, ec=col))
    ax.text(29, y + 2.5, title, color="white", ha="center", va="center", fontsize=9.5, fontweight="bold")
    ax.text(29, y - 3.2, textwrap.fill(desc, 30), color="white", ha="center", va="center", fontsize=6.2)
    ax.plot([14.4, 19.7], [50, y], color=MUTED, lw=1)
    k = len(tabs)
    ty = np.linspace(y + 7.2, y - 7.2, k) if k > 1 else [y]
    for t, yy in zip(tabs, ty):
        ax.plot([38.3, 42], [y, yy], color=MUTED, lw=0.8)
        ax.add_patch(FancyBboxPatch((42, yy - 2.9), 17, 5.8, boxstyle="round,pad=0.15", fc="white", ec=col, lw=1.4))
        ax.text(50.5, yy + 0.8, NAME[t], ha="center", va="center", fontsize=8.5, fontweight="bold", color=INK)
        ax.text(50.5, yy - 1.5, f"{n(real_rows[t])} dòng", ha="center", va="center", fontsize=7, color=INK2)
        txt = "\n".join(f"{c} = {v}" for c, v in ex_vals[t])
        ax.plot([59.2, 62], [yy, yy], color=MUTED, lw=0.8)
        ax.text(62.5, yy, txt, ha="left", va="center", fontsize=7.2, color=INK, family="monospace")
ax.set_title("Cây phân loại dữ liệu (data taxonomy): 11 bảng nguồn thuộc 4 nhóm, kèm giá trị thật của hai cột tiêu biểu", loc="left", fontsize=11.5)
f_tax = save(fig, "2-4_data_taxonomy")

# classification by data type, sensitivity, volatility
CLASS = [
    ("customers", "định danh (khách, vị trí thành phố/bang)", "nhạy cảm vừa: mã khách đã ẩn danh, có vị trí", "thấp (đổi khi khách đổi địa chỉ)"),
    ("sellers", "định danh (seller, vị trí)", "nhạy cảm vừa: mã seller ẩn danh, có vị trí", "thấp"),
    ("products", "thuộc tính (danh mục, kích thước)", "không nhạy cảm", "thấp"),
    ("orders", "thời gian và trạng thái", "nhạy cảm thấp: gắn với khách qua customer_id", "cao (trạng thái đổi theo từng mốc)"),
    ("order_items", "số tiền và khoá", "thông tin thương mại (giá, phí)", "thấp (ghi một lần)"),
    ("order_payments", "số tiền, hình thức", "thông tin thanh toán (đã tổng hợp, không có số thẻ)", "thấp"),
    ("order_reviews", "điểm số và văn bản tự do", "nhạy cảm vừa: văn bản có thể nêu thông tin cá nhân", "thấp (hiếm khi sửa)"),
    ("mql", "ngày, kênh (phân loại)", "thông tin kinh doanh nội bộ", "thấp"),
    ("closed_deals", "phân loại và số liệu doanh nghiệp seller", "thông tin kinh doanh nội bộ", "thấp"),
    ("geolocation", "vị trí (vĩ độ, kinh độ)", "vị trí: chỉ ở mức mã bưu chính", "rất thấp (tĩnh)"),
    ("category_translation", "văn bản tra cứu", "không nhạy cảm", "rất thấp (tĩnh)"),
]
class_df = pd.DataFrame([(NAME[t], next(g[0] for g in GROUPS if t in g[2]), a, b, c) for t, a, b, c in CLASS],
                        columns=["Bảng", "Nhóm", "Kiểu dữ liệu", "Độ nhạy cảm", "Tính biến động"])

# ----------------------------------------------------------------------------- LaTeX tables
def esc(s: str) -> str:
    return str(s).replace("\\", "\\textbackslash{}").replace("_", "\\_").replace("&", "\\&").replace("%", "\\%").replace("#", "\\#").replace("→", "$\\rightarrow$")


def tex_table(df: pd.DataFrame, caption: str, label: str, widths: list[str], code_cols: list[int] = (0,)) -> str:
    head = " & ".join("\\textbf{%s}" % esc(c) for c in df.columns) + "\\\\\\midrule"
    body = []
    for r in df.itertuples(index=False):
        cells = [("\\code{%s}" % esc(v)) if i in code_cols else esc(v) for i, v in enumerate(r)]
        body.append(" & ".join(cells) + "\\\\")
    cols = "".join("p{%s}" % w for w in widths)
    return ("\\begin{table}[htbp]\\centering\\scriptsize\\caption{%s}\\label{%s}\n\\begin{tabular}{%s}\\toprule\n%s\n%s\n\\bottomrule\\end{tabular}\\end{table}\n"
            % (caption, label, cols, head, "\n".join(body)))


TABLES_DIR.mkdir(exist_ok=True)
(TABLES_DIR / "p8_source_frequency.tex").write_text(
    tex_table(freq_df, "Tần suất cập nhật và công nghệ xử lý đề xuất cho từng bảng nguồn (cửa sổ 01/2017--08/2018)", "tab:tan-suat", ["2.9cm", "1.5cm", "2.2cm", "3.6cm", "4.6cm"]), encoding="utf-8")
(TABLES_DIR / "p8_source_taxonomy.tex").write_text(
    tex_table(class_df, "Phân loại 11 bảng nguồn theo kiểu dữ liệu, độ nhạy cảm và tính biến động", "tab:taxonomy", ["2.8cm", "2.3cm", "3.3cm", "3.9cm", "2.5cm"], code_cols=(0,)), encoding="utf-8")
print("tables written")

# ----------------------------------------------------------------------------- handoff md
o_all = daily["orders"]
md = ["# P8-C1 – Dữ liệu nguồn: tần suất cập nhật và data taxonomy (14/11/2026)",
      "", source_note("source_profile.py"), "",
      f"Cửa sổ tính trung bình và đỉnh: **{W0} → {W1}** ({n(N_DAYS)} ngày, giai đoạn chứa 99,6% số đơn). Toàn bộ dữ liệu đơn: {o_all.index.min():%d/%m/%Y} → {o_all.index.max():%d/%m/%Y}.", "",
      "## 1. Tần suất cập nhật và công nghệ xử lý đề xuất", "", md_table(freq_df, ["Trung bình / ngày"]), "",
      f"![Tần suất cập nhật]({f_freq.replace('figures/', '../figures/')})", "",
      f"- Đơn hàng trung bình {n(stats('orders')[0], 1)} đơn/ngày, đỉnh {n(stats('orders')[1])} đơn vào {stats('orders')[2]} (Black Friday); đỉnh gấp {n(stats('orders')[1] / stats('orders')[0], 1)} lần trung bình. Khối lượng này nhỏ: lô hằng ngày bằng procedure PostgreSQL xử lý trong vài giây, nên CDC + Kafka chỉ cần khi đòi hỏi gần thời gian thực.",
      "", "## 2. Data taxonomy", "",
      f"![Data taxonomy]({f_tax.replace('figures/', '../figures/')})", "", md_table(class_df), ""]
write_md("2026-11-14-P8-source.md", md)
