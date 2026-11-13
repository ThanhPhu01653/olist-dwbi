"""P8-D4: descriptive statistics (mean, median, std, skew, kurtosis, min, max).
1. Full data (olist_full): price, freight_value, product_weight_g, payment_value, lead time, delay, review_score -> report table.
2. The 5,000-order Excel sample (exports/eda_sample.xlsx): the same statistics computed in Python, written to a new sheet 'python_doi_chieu'
   so the group can compare with the output of Excel Data Analysis ToolPak (std = sample std, n-1; skew/kurt = Excel SKEW/KURT definitions).
-> handoff/2026-11-14-P8-eda.md (section describe), report/tables/p8_describe.tex, handoff/excel-toolpak-guide.md (section P8)
"""
from __future__ import annotations

from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill

from p8_common import *  # noqa: F401,F403

XLSX = ROOT / "exports" / "eda_sample.xlsx"
GUIDE = HANDOFF_DIR / "excel-toolpak-guide.md"
STATS = ["Mean", "Median", "Std", "Skew", "Kurtosis", "Min", "Max"]


def desc(s: pd.Series) -> dict:
    s = s.dropna().astype(float)
    # pandas skew() and kurt() are the bias-adjusted sample statistics, identical to Excel SKEW() and KURT() (excess kurtosis)
    return {"n": len(s), "Mean": s.mean(), "Median": s.median(), "Std": s.std(ddof=1), "Skew": s.skew(), "Kurtosis": s.kurt(), "Min": s.min(), "Max": s.max()}


# ---- 1. full data
items = items_df()
orders = orders_df()
pay = q("SELECT payment_value FROM oltp.order_payments")
FULL = [("Giá dòng hàng (price, BRL)", items["price"]), ("Phí vận chuyển (freight_value, BRL)", items["freight_value"]), ("Cân nặng (g)", items["product_weight_g"]),
        ("Giá trị thanh toán (BRL)", pay["payment_value"]), ("Lead time (ngày)", orders["lead_days"]), ("Số ngày trễ so với dự kiến", orders["delay_days"]), ("Điểm review", orders["review_score"])]
full = pd.DataFrame([{"Biến": k, **desc(v)} for k, v in FULL])

# ---- 2. Excel sample
sample = pd.read_excel(XLSX, sheet_name="du_lieu")
num = sample.iloc[:, 7:21]
ref = pd.DataFrame({c: desc(num[c]) for c in num.columns}).T
ref.index.name = "Biến"

wb = load_workbook(XLSX)
if "python_doi_chieu" in wb.sheetnames:
    del wb["python_doi_chieu"]
ws = wb.create_sheet("python_doi_chieu")
hdr = ["Biến", "n", "Mean", "Median", "Std (n-1)", "Skewness", "Kurtosis (excess)", "Min", "Max"]
ws.append(hdr)
for c in ws[1]:
    c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="1F4E79")
for name, r in ref.iterrows():
    ws.append([name, int(r["n"]), *[float(round(r[k], 6)) for k in STATS]])
ws.append([])
ws.append(["Ghi chú: số tính bằng Python (pandas) trên đúng 5.000 dòng của sheet du_lieu; Std là độ lệch chuẩn mẫu (n-1); Skewness và Kurtosis theo định nghĩa của hàm SKEW và KURT của Excel (đã hiệu chỉnh chệch, kurtosis là excess)."])
ws.append(["Dùng để đối chiếu với kết quả Data Analysis > Descriptive Statistics (Std = Standard Deviation, Skewness, Kurtosis)."])
ws.column_dimensions["A"].width = 18
for col in "BCDEFGHI":
    ws.column_dimensions[col].width = 16
ws.freeze_panes = "A2"
wb.save(XLSX)
print("sheet python_doi_chieu written")

# ---- tex table (full data)
def esc(s):
    return str(s).replace("_", "\\_").replace("%", "\\%")


def f(x, d=2):
    return n(x, d)


rows = "\n".join(f"{esc(r['Biến'])} & {f(r['Mean'])} & {f(r['Median'])} & {f(r['Std'])} & {f(r['Skew'])} & {f(r['Kurtosis'])} & {f(r['Min'])} & {f(r['Max'])}\\\\" for _, r in full.iterrows())
(ROOT / "report" / "tables" / "p8_describe.tex").write_text(
    "\\begin{table}[htbp]\\centering\\scriptsize\\caption{Thống kê đặc trưng của các biến số chính (toàn bộ dữ liệu nguồn)}\\label{tab:describe}\n"
    "\\begin{tabular}{p{4.3cm}rrrrrrr}\\toprule\n\\textbf{Biến} & \\textbf{TB} & \\textbf{Trung vị} & \\textbf{Độ lệch chuẩn} & \\textbf{Skewness} & \\textbf{Kurtosis} & \\textbf{Min} & \\textbf{Max}\\\\\\midrule\n"
    + rows + "\n\\bottomrule\\end{tabular}\\end{table}\n", encoding="utf-8")

# ---- handoff
show = full.copy()
for c in STATS:
    show[c] = show[c].map(lambda x: f(x))
show["n"] = show["n"].map(n)
price, frt = full.iloc[0], full.iloc[1]
md = [
    "Thống kê trên **toàn bộ dữ liệu nguồn** (`olist_full`); độ lệch chuẩn là độ lệch mẫu (n − 1), skewness và kurtosis theo định nghĩa Excel (kurtosis là kurtosis dư, bằng 0 với phân phối chuẩn).", "",
    md_table(show[["Biến", "n"] + STATS], ["n"] + STATS), "",
    f"- Giá và phí vận chuyển lệch phải mạnh: giá có trung bình {f(price['Mean'])} lớn hơn trung vị {f(price['Median'])} và skewness {f(price['Skew'])}; kurtosis {f(price['Kurtosis'])} cho thấy đuôi rất dày (nhiều ngoại lai hợp lệ, xem D1).",
    f"- Phí vận chuyển có trung bình {f(frt['Mean'])}, trung vị {f(frt['Median'])}, skewness {f(frt['Skew'])}.",
    f"- Điểm review có skewness {f(full.iloc[6]['Skew'])} (âm: tập trung ở điểm cao) và trung vị {f(full.iloc[6]['Median'])}; số ngày trễ có trung vị {f(full.iloc[5]['Median'])} (âm: phần lớn đơn giao sớm hơn dự kiến).",
    "- Vì phân phối lệch, báo cáo dùng **trung vị** cùng trung bình khi mô tả giá, phí và thời gian.", "",
    "### Số tính bằng Python để đối chiếu với Excel ToolPak (mẫu 5.000 đơn)", "",
    f"Sheet `python_doi_chieu` trong `exports/eda_sample.xlsx` chứa mean, median, std, skewness, kurtosis, min, max của 14 cột số của sheet `du_lieu`. Ví dụ: {', '.join(f'{k}: TB {f(ref.loc[k, 'Mean'])}, std {f(ref.loc[k, 'Std'])}' for k in ['price_total', 'lead_days', 'review_score'])}.", "",
]
section("describe", md)

# ---- ToolPak guide: add (or replace) the comparison section
g = GUIDE.read_text(encoding="utf-8")
block = ["<!-- p8:start -->", "## Đối chiếu với số tính bằng Python (P8)", "",
         "Sheet **python_doi_chieu** trong `exports/eda_sample.xlsx` (thêm ở P8, sinh bởi `scripts/eda/p8_describe.py`) chứa số đã tính sẵn bằng Python trên đúng 5.000 dòng của sheet `du_lieu`. Sau khi chạy **Descriptive Statistics** ở Bước 1, đối chiếu từng biến:", "",
         "| Excel ToolPak | Cột trong python_doi_chieu | Ghi chú |", "| --- | --- | --- |",
         "| Mean | Mean | khớp đến chữ số thập phân hiển thị |", "| Median | Median | |", "| Standard Deviation | Std (n-1) | ToolPak dùng độ lệch chuẩn mẫu (n − 1) |",
         "| Skewness | Skewness | cùng định nghĩa với hàm SKEW của Excel |", "| Kurtosis | Kurtosis (excess) | cùng định nghĩa với hàm KURT; bằng 0 với phân phối chuẩn |", "| Minimum / Maximum | Min / Max | |", "",
         "Số khớp với bảng đối chiếu ở Bước 1 (ví dụ price_total: trung bình " + f(ref.loc['price_total', 'Mean']) + ", độ lệch chuẩn " + f(ref.loc['price_total', 'Std']) + ").", "",
         "Bảng thống kê đặc trưng trên **toàn bộ dữ liệu** (không chỉ mẫu) nằm ở `handoff/2026-11-14-P8-eda.md`, mục D4.", "<!-- p8:end -->"]
import re as _re

if "<!-- p8:start -->" in g:
    g = _re.sub(r"<!-- p8:start -->.*?<!-- p8:end -->", lambda m: "\n".join(block), g, flags=_re.S)
else:
    g = g.rstrip("\n") + "\n\n" + "\n".join(block) + "\n"
GUIDE.write_text(g, encoding="utf-8")
print("guide updated")
