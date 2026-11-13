"""P8b: report tables for chapter 4 from the dashboard design (scripts/gen_dashboard_docs.py) and powerbi/measures.md
-> report/tables/p8b_dashboard_stats.tex (pages, visuals, slicers, measures per dashboard, DESIGN numbers) and p8b_dashboard_matrix.tex (checklist x DB1-DB4)
   python scripts/p8b_dashboard_tables.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import gen_dashboard_docs as g  # noqa: E402

T = ROOT / "report" / "tables"
lines = (ROOT / "powerbi" / "measures.md").read_text(encoding="utf-8").splitlines()
sec = {}
cur = None
for l in lines:
    m = re.match(r"## ([1-4])\. (DB\d)", l)
    if m:
        cur = m.group(2)
        sec[cur] = 0
    elif l.startswith("## "):
        cur = None
    elif cur and l.startswith("### "):
        sec[cur] += 1


def esc(x: str) -> str:
    return str(x).replace("_", "\\_").replace("&", "\\&").replace("%", "\\%")


rows = []
for key, d in g.DB.items():
    main_pages = len(d["pages"]) + sum(1 for t, _ in d["extra_pages"] if "tooltip" not in t.lower())
    tooltips = sum(1 for t, _ in d["extra_pages"] if "tooltip" in t.lower())
    vis = 0
    for _, src, pg in d["pages"]:
        vis += len(g.grid_rows(src, pg))
    for _, r in d["extra_pages"]:
        vis += sum(1 for x in r if x[2] not in ("Button", "Văn bản"))
    sl = []
    for s_ in d["sources"]:
        sl += [x for x in g.SRC[s_]["slicers"] if x not in sl]
    nslicer = len(sl) + len(d["slicer_hier"])
    rows.append((d["title"], d["kind"], main_pages, tooltips, vis, nslicer, sec.get(key, 0)))
tot = [sum(r[i] for r in rows) for i in (2, 3, 4, 5, 6)]

body = "\n".join(f"{esc(a)} & {esc(b)} & {c} & {t} & {v} & {s_} & {m}\\\\" for a, b, c, t, v, s_, m in rows)
(T / "p8b_dashboard_stats.tex").write_text(
    "\\begin{table}[htbp]\\centering\\scriptsize\\caption{Thống kê bộ dashboard theo thiết kế (số thật thay vào sau khi dựng)}\\label{tab:dash-thong-ke}\n"
    "\\begin{tabular}{p{4.0cm}p{3.6cm}rrrrr}\\toprule\n\\textbf{Dashboard} & \\textbf{Loại} & \\textbf{Trang} & \\textbf{Tooltip} & \\textbf{Visual} & \\textbf{Slicer} & \\textbf{Measure}\\\\\\midrule\n"
    + body + f"\n\\midrule\n\\textbf{{Tổng}} & & {tot[0]} & {tot[1]} & {tot[2]} & {tot[3]} & {tot[4]}\\\\\n\\bottomrule\\end{{tabular}}\\\\[2pt]"
    "{\\footnotesize Visual: số dòng của bảng bố cục trong hướng dẫn từng dashboard (DB*.md); slicer: số slicer và bộ lọc khác nhau của dashboard; measure: số measure định nghĩa ở mục tương ứng của \\code{powerbi/measures.md} (measure dùng chung chỉ tính một lần).}\n\\end{table}\n",
    encoding="utf-8")

head = " & ".join(["\\textbf{Mục checklist}"] + [f"\\textbf{{{k}}}" for k in g.DB]) + "\\\\\\midrule"
mat = "\n".join(" & ".join([esc(g.ITEMS[i][0])] + ["Có" if g.MATRIX[k][i] else "--" for k in g.DB]) + "\\\\" for i in range(len(g.ITEMS)))
(T / "p8b_dashboard_matrix.tex").write_text(
    "\\begin{table}[htbp]\\centering\\scriptsize\\caption{Ma trận checklist theo dashboard (Có: đáp ứng; --: không áp dụng)}\\label{tab:dash-checklist}\n"
    f"\\begin{{tabular}}{{p{{5.6cm}}cccc}}\\toprule\n{head}\n{mat}\n\\bottomrule\\end{{tabular}}\\end{{table}}\n", encoding="utf-8")
print("rows:", rows, "total", tot)
