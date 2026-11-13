"""P8-C1/E1: layer tables from the database -> report/tables/p8_layers.tex (components, technology, tables, rows, frequency)
and report/tables/p8_dataflow_layers.tex (proposed data flow table without counts) + handoff/2026-11-14-P8-layers.md.   python scripts/p8_layers.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "eda"))

import pandas as pd
from sqlalchemy import text

from etl import config
from etl.db import get_engine

TABLES = ROOT / "report" / "tables"
eng = get_engine(config.DB_NAME)


def counts(schema: str) -> tuple[int, int]:
    with eng.connect() as c:
        names = [r[0] for r in c.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema=:s AND table_type='BASE TABLE'"), {"s": schema})]
        total = sum(c.execute(text(f'SELECT count(*) FROM "{schema}"."{t}"')).scalar_one() for t in names)
    return len(names), total


def views(schemas: list[str]) -> tuple[int, int]:
    with eng.connect() as c:
        v = c.execute(text("SELECT count(*) FROM information_schema.views WHERE table_schema = ANY(:s)"), {"s": schemas}).scalar_one()
        m = c.execute(text("SELECT count(*) FROM pg_matviews WHERE schemaname = ANY(:s)"), {"s": schemas}).scalar_one()
    return v + m, m


def n(x: int) -> str:
    return f"{x:,}".replace(",", ".")


oltp, crm, stg, ods, dw, log = counts("oltp"), counts("crm"), counts("staging"), counts("ods"), counts("dw"), counts("etl_log")
marts = ["mart_sales", "mart_fulfillment", "mart_cx", "mart_acquisition"]
nviews, nmat = views(marts)
dwviews = views(["dw"])[0]

ROWS = [
    ("Nguồn", "oltp (9 bảng), crm (2 bảng)", "PostgreSQL 18; nạp từ 11 file CSV bằng Python (COPY)", str(oltp[0] + crm[0]), n(oltp[1] + crm[1]), "mô phỏng cập nhật theo tháng (ban đầu đến 31/12/2017, rồi 11 đợt)", "hai hệ thống độc lập, chỉ gặp nhau qua seller\\_id"),
    ("Staging", "stg\\_* (bản sao thô)", "PostgreSQL; extract bằng Python + SQL", str(stg[0]), n(stg[1]), "mỗi lần chạy pipeline (full hoặc incremental)", "thêm mã lô nạp và thời điểm nạp để truy vết"),
    ("ODS", "ods.* (dữ liệu sạch, cờ chất lượng)", "PostgreSQL procedure (PL/pgSQL)", str(ods[0]), n(ods[1]), "mỗi lần chạy pipeline", "dòng lỗi ghi \\code{rejected\\_rows}, không xoá âm thầm"),
    ("Kho dữ liệu", "dw: 10 dimension + 6 fact", "PostgreSQL procedure; khoá thay thế, SCD1/SCD2", str(dw[0]), n(dw[1]), "mỗi lần chạy pipeline; nạp tăng dần theo watermark", f"{dwviews} view đóng vai cho \\code{{dim\\_date}}"),
    ("Data mart", "mart\\_sales, mart\\_fulfillment, mart\\_cx, mart\\_acquisition", "PostgreSQL view và materialized view", f"{nviews} view ({nmat} materialized)", "--", "làm mới materialized view mỗi lần chạy", "tổng hợp sẵn cho dashboard DB1--DB4"),
    ("Giám sát", "etl\\_log: job\\_run, rejected\\_rows, dq\\_check...", "PostgreSQL; Python ghi log", str(log[0]), n(log[1]), "ghi ở mọi bước", "nguồn cho bảng giám sát ở mục 3.3"),
    ("BI", "37 file CSV, mô hình ngữ nghĩa, 4 dashboard", "Python xuất CSV; Power BI Desktop (Import, DAX)", "--", "--", "làm mới sau mỗi lần xuất CSV", "Publish to web"),
]
df = pd.DataFrame(ROWS, columns=["Lớp", "Thành phần", "Công nghệ", "Số bảng", "Số dòng", "Tần suất", "Ghi chú"])


def tex(df: pd.DataFrame, caption: str, label: str, widths: list[str]) -> str:
    head = " & ".join("\\textbf{%s}" % c for c in df.columns) + "\\\\\\midrule"
    body = "\n".join(" & ".join(map(str, r)) + "\\\\" for r in df.itertuples(index=False))
    ws = [float(w.replace("cm", "")) for w in widths]
    cols = "".join("p{%.2fcm}" % (x * (15.7 - 0.42 * len(ws)) / sum(ws)) for x in ws)
    return f"\\begin{{table}}[htbp]\\centering\\scriptsize\\caption{{{caption}}}\\label{{{label}}}\n\\begin{{tabular}}{{{cols}}}\\toprule\n{head}\n{body}\n\\bottomrule\\end{{tabular}}\\end{{table}}\n"


TABLES.mkdir(exist_ok=True)
(TABLES / "p8_layers.tex").write_text(tex(df, "Các lớp của kiến trúc: thành phần, công nghệ, số bảng, số dòng và tần suất (trạng thái cuối)", "tab:p8-layers", ["1.5cm", "3.0cm", "3.0cm", "1.4cm", "1.6cm", "2.6cm", "2.6cm"]), encoding="utf-8")
(TABLES / "p8_dataflow_layers.tex").write_text(
    tex(df.drop(columns=["Số bảng", "Số dòng"]), "Luồng dữ liệu đề xuất: lớp, thành phần, công nghệ, tần suất và ghi chú", "tab:p8-dataflow", ["1.6cm", "3.6cm", "3.6cm", "3.2cm", "3.2cm"]), encoding="utf-8")

md = ["# P8 – Các lớp của kiến trúc (số liệu từ olist_dw)", "", "*Sinh tự động bởi `scripts/p8_layers.py`.*", "",
      "| Lớp | Thành phần | Công nghệ | Số bảng | Số dòng | Tần suất | Ghi chú |", "| --- | --- | --- | ---: | ---: | --- | --- |"]
for r in df.itertuples(index=False):
    md.append("| " + " | ".join(re.sub(r"\\code\{([^}]*)\}", r"`\1`", str(v)).replace("\\_", "_") for v in r) + " |")
(ROOT / "handoff" / "2026-11-14-P8-layers.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print(df[["Lớp", "Số bảng", "Số dòng"]].to_string(index=False))
