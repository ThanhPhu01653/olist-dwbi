"""P8-E3: conceptual dimension hierarchy tables (columns = hierarchy levels, cells = real example values, last row = distinct count per level),
hierarchy correctness checks, and the grouping of the 10 dimensions.  Reads olist_dw.
-> report/tables/p8_dim_hier.tex, p8_dim_checks.tex, p8_dim_groups.tex, handoff/2026-11-14-P8-dimensions.md
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
from sqlalchemy import text

from etl import config
from etl.db import get_engine

eng = get_engine(config.DB_NAME)


def q(sql: str) -> pd.DataFrame:
    with eng.connect() as c:
        return pd.read_sql_query(text(sql), c)


def n(x) -> str:
    return f"{int(x):,}".replace(",", ".")


def esc(s) -> str:
    return str(s).replace("_", "\\_").replace("&", "\\&").replace("%", "\\%").replace("#", "\\#")


# --------------------------------------------------------------------------- hierarchies
H = []  # (dim, title, DataFrame of rows with the level columns, level labels, distinct counts)


def add(dim: str, title: str, df: pd.DataFrame, labels: list[str], counts: list[int], examples: pd.DataFrame, note: str = "") -> None:
    H.append(dict(dim=dim, title=title, labels=labels, counts=counts, examples=examples, note=note))


# dim_date: Year -> Quarter -> Month -> Day
d = q("SELECT year, year_quarter, year_month, full_date::text AS day, month FROM dw.dim_date WHERE date_key <> -1")
ex = q("SELECT year, year_quarter, year_month, full_date::text AS day FROM dw.dim_date WHERE full_date IN ('2017-11-24','2018-03-15','2016-12-25') ORDER BY full_date")
add("dim_date", "Chiều thời gian: Năm → Quý → Tháng → Ngày", d, ["Năm", "Quý", "Tháng", "Ngày"], [d.year.nunique(), d.year_quarter.nunique(), d.year_month.nunique(), d.day.nunique()], ex)
n_month_alone, n_year_month = d.month.nunique(), d.year_month.nunique()

# dim_geography: Region -> State -> City -> Zip
g = q("SELECT region, state_code, city, zip_code_prefix FROM dw.dim_geography WHERE geography_key <> -1")
ex = q("""SELECT region, state_code, city, min(zip_code_prefix) AS zip FROM dw.dim_geography WHERE geography_key <> -1 AND (state_code, city) IN (('SP','sao paulo'),('BA','salvador'),('RS','porto alegre'))
          GROUP BY 1,2,3 ORDER BY 2""")
add("dim_geography", "Chiều địa lý: Vùng → Bang → Thành phố → Mã bưu chính", g, ["Vùng", "Bang", "Thành phố (kèm bang)", "Mã bưu chính"],
    [g.region.nunique(), g.state_code.nunique(), len(g[["state_code", "city"]].drop_duplicates()), g.zip_code_prefix.nunique()], ex)
city_names = g.city.nunique()
pairs = len(g[["state_code", "city"]].drop_duplicates())
multi = g.groupby("city").state_code.nunique()
dup_names = int((multi > 1).sum())
dup_example = multi.sort_values(ascending=False).head(3)

# dim_product: Group -> Category -> Product
p = q("SELECT category_group, category_name_en, product_id FROM dw.dim_product WHERE product_key <> -1")
ex = q("""SELECT DISTINCT ON (category_group) category_group, category_name_en, left(product_id, 8) AS product FROM dw.dim_product WHERE product_key <> -1
          AND category_name_en IN ('health_beauty','computers_accessories','bed_bath_table') ORDER BY category_group, product_id""")
add("dim_product", "Chiều sản phẩm: Nhóm ngành → Danh mục → Sản phẩm", p, ["Nhóm ngành hàng", "Danh mục (tiếng Anh)", "Sản phẩm (product_id)"],
    [p.category_group.nunique(), p.category_name_en.nunique(), p.product_id.nunique()], ex)
cat_multi_group = int((p.groupby("category_name_en").category_group.nunique() > 1).sum())

# dim_seller: Region -> State -> City -> Seller ; Channel -> Origin
s = q("""SELECT g.region, s.state_code, s.city, s.seller_id, s.acquisition_channel, s.acquisition_origin FROM dw.dim_seller s JOIN dw.dim_geography g USING (geography_key)
         WHERE s.seller_key <> -1""")
ex = q("""SELECT g.region, s.state_code, s.city, left(s.seller_id, 8) AS seller FROM dw.dim_seller s JOIN dw.dim_geography g USING (geography_key)
          WHERE s.seller_key <> -1 AND (s.state_code, s.city) IN (('SP','sao paulo'),('MG','belo horizonte'),('PR','curitiba')) ORDER BY s.state_code, s.seller_id""")
ex = ex.groupby("state_code", as_index=False).first()[["region", "state_code", "city", "seller"]]
add("dim_seller", "Chiều seller: Vùng → Bang → Thành phố → Seller", s, ["Vùng", "Bang", "Thành phố (kèm bang)", "Seller"],
    [s.region.nunique(), s.state_code.nunique(), len(s[["state_code", "city"]].drop_duplicates()), s.seller_id.nunique()], ex, "Có thêm phân cấp kênh thu hút: Kênh → Origin → Seller (xem dim_lead_origin).")

# dim_customer: Region -> State -> City -> Zip -> Customer -> Version
c = q("""SELECT g.region, c.state_code, c.city, c.zip_code_prefix, c.customer_unique_id, c.customer_key FROM dw.dim_customer c JOIN dw.dim_geography g USING (geography_key)
         WHERE c.customer_key <> -1""")
ex = q("""SELECT g.region, c.state_code, c.city, c.zip_code_prefix AS zip, left(c.customer_unique_id, 8) AS khach, c.version_no AS ver
          FROM dw.dim_customer c JOIN dw.dim_geography g USING (geography_key) WHERE c.customer_key <> -1 AND c.is_current AND (c.state_code, c.city) IN (('SP','sao paulo'),('RJ','rio de janeiro'),('MG','belo horizonte'))
          ORDER BY c.state_code, c.customer_key""")
ex = ex.groupby("state_code", as_index=False).first()[["region", "state_code", "city", "zip", "khach", "ver"]]
add("dim_customer", "Chiều khách hàng (SCD loại 2): Vùng → Bang → Thành phố → Mã bưu chính → Khách → Phiên bản", c, ["Vùng", "Bang", "Thành phố (kèm bang)", "Mã bưu chính", "Khách thật", "Phiên bản (dòng)"],
    [c.region.nunique(), c.state_code.nunique(), len(c[["state_code", "city"]].drop_duplicates()), c.zip_code_prefix.nunique(), c.customer_unique_id.nunique(), c.customer_key.nunique()], ex)

# small hierarchies
lo = q("SELECT channel_group, origin FROM dw.dim_lead_origin WHERE lead_origin_key <> -1 ORDER BY 1, 2")
ex = lo.groupby("channel_group", as_index=False).first().head(3)
add("dim_lead_origin", "Chiều kênh thu hút: Nhóm kênh → Origin", lo, ["Nhóm kênh", "Origin"], [lo.channel_group.nunique(), lo.origin.nunique()], ex)
origin_multi = int((lo.groupby("origin").channel_group.nunique() > 1).sum())
os_ = q("SELECT status_group, order_status FROM dw.dim_order_status WHERE order_status_key <> -1 ORDER BY 1, 2")
add("dim_order_status", "Chiều trạng thái đơn: Nhóm trạng thái → Trạng thái", os_, ["Nhóm trạng thái", "Trạng thái đơn"], [os_.status_group.nunique(), os_.order_status.nunique()], os_.groupby("status_group", as_index=False).first())
pt = q("SELECT payment_group, payment_type FROM dw.dim_payment_type WHERE payment_type_key <> -1 ORDER BY 1, 2")
add("dim_payment_type", "Chiều hình thức thanh toán: Nhóm → Hình thức", pt, ["Nhóm thanh toán", "Hình thức"], [pt.payment_group.nunique(), pt.payment_type.nunique()], pt.groupby("payment_group", as_index=False).first())
sr = q("SELECT rep_role, left(rep_id, 8) AS rep FROM dw.dim_sales_rep WHERE sales_rep_key <> -1 ORDER BY 1, rep_id")
add("dim_sales_rep", "Chiều nhân viên sales: Vai trò → Nhân viên", sr, ["Vai trò", "Nhân viên"], [sr.rep_role.nunique(), len(sr)], sr.groupby("rep_role", as_index=False).first())

# --------------------------------------------------------------------------- LaTeX: hierarchy tables
def hier_tex(h: dict) -> str:
    cols = h["labels"]
    ex = h["examples"].astype(str).values.tolist()
    spec = "l" * len(cols)
    head = " & ".join("\\textbf{%s}" % esc(x) for x in cols) + "\\\\\\midrule"
    body = "\n".join(" & ".join(esc(v) for v in r[: len(cols)]) + "\\\\" for r in ex)
    cnt = " & ".join("\\textbf{%s}" % n(x) for x in h["counts"])
    return (f"\\begin{{table}}[htbp]\\centering\\scriptsize\\caption{{{esc(h['title'])}}}\\label{{tab:hier-{h['dim'].replace('_', '-')}}}\n\\begin{{tabular}}{{{spec}}}\\toprule\n{head}\n{body}\n\\midrule\n"
            f"{cnt}\\\\\n\\multicolumn{{{len(cols)}}}{{l}}{{\\footnotesize\\emph{{Dòng cuối: số giá trị phân biệt của từng cấp (không tính dòng Unknown).}}}}\\\\\n\\bottomrule\\end{{tabular}}\\end{{table}}\n")


tables = ROOT / "report" / "tables"
(tables / "p8_dim_hier.tex").write_text("\n".join(hier_tex(h) for h in H), encoding="utf-8")

# --------------------------------------------------------------------------- checks
state_region_multi = int((g.groupby("state_code").region.nunique() > 1).sum())
zip_city_multi = int(q("SELECT count(*) FROM (SELECT zip_code_prefix FROM dw.dim_geography WHERE geography_key <> -1 GROUP BY 1 HAVING count(DISTINCT city) > 1) t").iloc[0, 0])
zip_state_multi = int(q("SELECT count(*) FROM (SELECT zip_code_prefix FROM dw.dim_geography WHERE geography_key <> -1 GROUP BY 1 HAVING count(DISTINCT state_code) > 1) t").iloc[0, 0])
top_dup = ", ".join(f"{c} ({k} bang)" for c, k in dup_example.items())
CHECKS = [
    ("Tháng phải đi kèm năm", f"chỉ có {n(n_month_alone)} số tháng nhưng {n(n_year_month)} cặp (năm, tháng): tên tháng một mình không xác định một nút của phân cấp", "đúng: dùng year_month ('YYYY-MM') và year_quarter làm cấp, không dùng month một mình"),
    ("Thành phố phải đi kèm bang", f"{n(city_names)} tên thành phố nhưng {n(pairs)} cặp (bang, thành phố); {n(dup_names)} tên thành phố xuất hiện ở từ 2 bang trở lên (nhiều nhất: {top_dup})", "đúng: cấp thành phố luôn đi kèm bang; không gộp theo tên thành phố"),
    ("Mã bưu chính xác định một thành phố và một bang", f"{n(zip_city_multi)} mã có nhiều hơn một thành phố, {n(zip_state_multi)} mã có nhiều hơn một bang", "đúng: dim_geography có một dòng cho mỗi mã bưu chính"),
    ("Bang thuộc đúng một vùng", f"{n(state_region_multi)} bang thuộc nhiều hơn một vùng ({n(g.state_code.nunique())} bang, {n(g.region.nunique())} vùng)", "đúng: Vùng → Bang là quan hệ một nhiều"),
    ("Sản phẩm → danh mục → nhóm ngành", f"{n(cat_multi_group)} danh mục thuộc nhiều hơn một nhóm ngành ({n(p.category_name_en.nunique())} danh mục, {n(p.category_group.nunique())} nhóm ngành)", "đúng: mỗi danh mục một nhóm; sản phẩm chưa có danh mục vào nhóm unknown"),
    ("Origin → nhóm kênh", f"{n(origin_multi)} origin thuộc nhiều hơn một nhóm kênh ({n(lo.origin.nunique())} origin, {n(lo.channel_group.nunique())} nhóm kênh)", "đúng: mỗi origin một nhóm kênh"),
]
rows = "\n".join(f"{esc(a)} & {esc(b)} & {esc(c_)}\\\\" for a, b, c_ in CHECKS)
(tables / "p8_dim_checks.tex").write_text(
    "\\begin{table}[htbp]\\centering\\scriptsize\\caption{Kiểm tra tính đúng của các phân cấp (đếm từ kho dữ liệu)}\\label{tab:hier-checks}\n\\begin{tabular}{p{3.6cm}p{7.2cm}p{4.6cm}}\\toprule\n"
    "\\textbf{Phân cấp} & \\textbf{Kết quả đếm} & \\textbf{Kết luận}\\\\\\midrule\n" + rows + "\n\\bottomrule\\end{tabular}\\end{table}\n", encoding="utf-8")

# --------------------------------------------------------------------------- groups
rows_cnt = {r.t: int(r.n) for r in q("""SELECT 'dim_date' t, count(*) n FROM dw.dim_date UNION ALL SELECT 'dim_geography', count(*) FROM dw.dim_geography UNION ALL SELECT 'dim_customer', count(*) FROM dw.dim_customer
    UNION ALL SELECT 'dim_seller', count(*) FROM dw.dim_seller UNION ALL SELECT 'dim_product', count(*) FROM dw.dim_product UNION ALL SELECT 'dim_order_status', count(*) FROM dw.dim_order_status
    UNION ALL SELECT 'dim_payment_type', count(*) FROM dw.dim_payment_type UNION ALL SELECT 'dim_lead_origin', count(*) FROM dw.dim_lead_origin UNION ALL SELECT 'dim_lead_profile', count(*) FROM dw.dim_lead_profile
    UNION ALL SELECT 'dim_sales_rep', count(*) FROM dw.dim_sales_rep""").itertuples()}
fk = q("""SELECT ccu.table_name AS dim, count(DISTINCT tc.table_name) AS n_fact, string_agg(DISTINCT replace(tc.table_name, 'fact_', ''), ', ') AS facts
          FROM information_schema.table_constraints tc JOIN information_schema.constraint_column_usage ccu USING (constraint_schema, constraint_name)
          WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'dw' AND tc.table_name LIKE 'fact\\_%' AND ccu.table_name LIKE 'dim\\_%' GROUP BY 1""").set_index("dim")
GROUPS = [
    ("Chiều dùng chung (conformed)", "dim_date", "11 view đóng vai; dùng bởi mọi fact"),
    ("Chiều dùng chung (conformed)", "dim_geography", "zip → thành phố → bang → vùng; nối khách, seller"),
    ("Chiều dùng chung (conformed)", "dim_seller", "nối quy trình bán hàng với thu hút seller (SCD1)"),
    ("Chiều dùng chung (conformed)", "dim_customer", "SCD loại 2: giữ lịch sử mã bưu chính"),
    ("Chiều dùng chung (conformed)", "dim_order_status", "dùng bởi fact đơn hàng và fact xử lý đơn"),
    ("Chiều đóng vai (role-playing)", "dim_date", "mua, duyệt, bàn giao, giao, dự kiến, liên hệ, chốt, đơn đầu tiên..."),
    ("Chiều đóng vai (role-playing)", "dim_sales_rep", "một bảng cho hai vai trò: SDR và SR"),
    ("Chiều SCD loại 2", "dim_customer", "đóng phiên bản cũ, mở phiên bản mới khi đổi mã bưu chính"),
    ("Chiều rác (junk)", "dim_lead_profile", "gom 7 thuộc tính nhỏ của deal thành một chiều"),
    ("Danh mục nhỏ (lookup)", "dim_order_status", "trạng thái đơn → nhóm trạng thái"),
    ("Danh mục nhỏ (lookup)", "dim_payment_type", "hình thức thanh toán → nhóm"),
    ("Danh mục nhỏ (lookup)", "dim_lead_origin", "origin → nhóm kênh"),
    ("Chiều của một quy trình (một fact)", "dim_product", "sản phẩm → danh mục → nhóm ngành; chỉ fact_order_item dùng"),
]
grow = []
for grp, dim, note in GROUPS:
    nf = int(fk.loc[dim, "n_fact"]) if dim in fk.index else 0
    grow.append((grp, dim, n(rows_cnt[dim]), nf, note))
rows = "\n".join(f"{esc(a)} & \\code{{{esc(b)}}} & {c_} & {d_} & {esc(e)}\\\\" for a, b, c_, d_, e in grow)
(tables / "p8_dim_groups.tex").write_text(
    "\\begin{table}[htbp]\\centering\\scriptsize\\caption{Phân nhóm 10 bảng chiều (một chiều có thể thuộc nhiều nhóm)}\\label{tab:dim-groups}\n\\begin{tabular}{p{3.6cm}p{3.0cm}rrp{5.0cm}}\\toprule\n"
    "\\textbf{Nhóm} & \\textbf{Chiều} & \\textbf{Số dòng} & \\textbf{Số fact} & \\textbf{Ghi chú}\\\\\\midrule\n" + rows + "\n\\bottomrule\\end{tabular}\\end{table}\n", encoding="utf-8")

# --------------------------------------------------------------------------- markdown
md = ["# P8-E3 – Hệ thống chiều khái niệm (số liệu từ olist_dw)", "", "*Sinh tự động bởi `scripts/p8_dimensions.py`.*", ""]
for h in H:
    md += [f"## {h['title']}", "", "| " + " | ".join(h["labels"]) + " |", "| " + " | ".join("---" for _ in h["labels"]) + " |"]
    for r in h["examples"].astype(str).values.tolist():
        md.append("| " + " | ".join(r[: len(h["labels"])]) + " |")
    md += ["| " + " | ".join(f"**{n(x)}**" for x in h["counts"]) + " |", "", "(dòng cuối: số giá trị phân biệt của từng cấp)", ""]
md += ["## Kiểm tra phân cấp", "", "| Phân cấp | Kết quả đếm | Kết luận |", "| --- | --- | --- |"] + [f"| {a} | {b} | {c_} |" for a, b, c_ in CHECKS] + ["", "## Phân nhóm dimension", "", "| Nhóm | Chiều | Số dòng | Số fact | Ghi chú |", "| --- | --- | ---: | ---: | --- |"]
md += [f"| {a} | {b} | {c_} | {d_} | {e} |" for a, b, c_, d_, e in grow]
(ROOT / "handoff" / "2026-11-14-P8-dimensions.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("city names", city_names, "pairs", pairs, "dup names", dup_names, top_dup)
print("month alone", n_month_alone, "year_month", n_year_month, "cat multi group", cat_multi_group, "origin multi", origin_multi)
