"""P8-C3: OLTP -> OLAP mapping summary (per source table: columns, columns used in the warehouse, target dim/fact tables, example transformation)
-> report/tables/p8_mapping_summary.tex + handoff/2026-11-14-P8-mapping-summary.md.   python scripts/p8_mapping_summary.py
Derived from docs/mapping.csv (source -> ods and ods -> dw), so it follows whatever gen_mapping.py produced.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import pandas as pd
from sqlalchemy import text

from drawio_p8 import used_oltp_columns
from etl import config
from etl.db import get_engine

used, a = used_oltp_columns()
m = pd.read_csv(ROOT / "docs" / "mapping.csv", encoding="utf-8-sig")
b = m[m.layer == "ods → dw"]

eng = get_engine(config.DB_NAME_FULL)
with eng.connect() as c:
    real = {(f"{s}.{t}", col) for s, t, col in c.execute(text("SELECT table_schema, table_name, column_name FROM information_schema.columns WHERE table_schema IN ('oltp','crm')"))}
ncols = {}
for t_, _c in real:
    ncols[t_] = ncols.get(t_, 0) + 1

# ods table -> oltp table
ods_of = {}
for r in a.itertuples():
    ods_of.setdefault(r.source_table, set()).add(r.target_table)
rows = []
for src in sorted(ods_of, key=lambda s: (s.startswith("crm"), s)):
    ods_tabs = ods_of[src]
    targets = sorted({r.target_table.replace("dw.", "") for r in b.itertuples() if any(t in str(r.source_table) for t in ods_tabs)})
    n_used = sum(1 for (t, c_) in used if t == src and (t, c_) in real)  # skip ODS-only pseudo columns such as dq_flags
    ex = a[a.source_table == src]
    ex = ex[ex.transformation != "Giữ nguyên giá trị"].head(1)
    ex_txt = f"{ex.iloc[0].source_column} → {ex.iloc[0].target_column}: {ex.iloc[0].transformation}" if len(ex) else "giữ nguyên giá trị"
    rows.append((src, ncols[src], n_used, ", ".join(targets) or "–", ex_txt))
df = pd.DataFrame(rows, columns=["Bảng nguồn", "Số cột", "Cột dùng sang OLAP", "Bảng đích (dim, fact)", "Ví dụ phép biến đổi"])
tot_c, tot_u = int(df["Số cột"].sum()), int(df["Cột dùng sang OLAP"].sum())


def esc(s: str) -> str:
    s = str(s)
    for x, y in [("_", "\\_"), ("&", "\\&"), ("%", "\\%"), ("#", "\\#")]:
        s = s.replace(x, y)
    return s.replace("→", "$\\rightarrow$")


widths = [3.0, 1.0, 1.4, 5.0, 4.8]
k = (15.7 - 0.42 * len(widths)) / sum(widths)
spec = "".join("p{%.2fcm}" % (w * k) for w in widths)
head = " & ".join("\\textbf{%s}" % esc(c) for c in df.columns) + "\\\\\\midrule"
body = "\n".join(" & ".join(esc(v) for v in r) + "\\\\" for r in df.itertuples(index=False))
tail = "\\midrule\n\\textbf{Tổng} & %d & %d & & \\\\" % (tot_c, tot_u)
(ROOT / "report" / "tables" / "p8_mapping_summary.tex").write_text(
    "\\begin{table}[htbp]\\centering\\scriptsize\\caption{Tổng hợp mapping OLTP sang OLAP theo bảng nguồn}\\label{tab:mapping-tong-hop}\n"
    f"\\begin{{tabular}}{{{spec}}}\\toprule\n{head}\n{body}\n{tail}\n\\bottomrule\\end{{tabular}}\\end{{table}}\n", encoding="utf-8")

md = ["# P8-C3 – Tổng hợp mapping OLTP → OLAP", "", "*Sinh tự động bởi `scripts/p8_mapping_summary.py` từ `docs/mapping.csv`.*", "",
      "| " + " | ".join(df.columns) + " |", "| --- | ---: | ---: | --- | --- |"]
md += ["| " + " | ".join(str(v).replace("|", "\\|") for v in r) + " |" for r in df.itertuples(index=False)]
md += [f"| **Tổng** | {tot_c} | {tot_u} | | |", "", f"Cột dùng sang OLAP: {tot_u} / {tot_c} cột nguồn ({100 * tot_u / tot_c:.1f}%). Các cột không dùng sang OLAP: " + ", ".join(f"{t}.{c_}" for t, c_ in sorted(real - used)) + "."]
(ROOT / "handoff" / "2026-11-14-P8-mapping-summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print(df.to_string(index=False))
print("used", tot_u, "of", tot_c)
