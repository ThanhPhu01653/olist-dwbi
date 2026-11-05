"""Run sql/60_olap_examples/*.sql and write handoff/olap-examples.md (query, time, result table).

    python scripts/run_olap_examples.py

A file holds several queries, each introduced by a line  -- QUERY: <title>. Comment lines before the first QUERY are the explanation of the
OLAP operation. Every number in the output comes from the database.
"""
from __future__ import annotations

import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text

from etl import config
from etl.db import get_engine

ROLAP_TEXT = """## Vì sao đây là ROLAP, và khác MOLAP ở đâu
- **ROLAP (Relational OLAP)**: dữ liệu nằm trong bảng quan hệ theo lược đồ sao (`dim_*`, `fact_*` trong PostgreSQL); mỗi thao tác OLAP được dịch thành một câu SQL
  (`GROUP BY` / `ROLLUP` / `CUBE` / `GROUPING SETS`, `WHERE` cho slice và dice, `FILTER` cho pivot). Tổng hợp được tính lúc truy vấn (có thể tăng tốc bằng materialized view ở các mart).
- **MOLAP (Multidimensional OLAP)**: dữ liệu được nạp vào một khối đa chiều riêng (ví dụ SQL Server Analysis Services) với các tổng hợp **tính sẵn** và lưu dạng mảng; truy vấn rất nhanh nhưng
  cần bước xử lý (process) khối, tốn thêm dung lượng và khó cập nhật tăng dần khi chiều/measure đổi.
- **Chọn ROLAP** vì dự án dùng PostgreSQL (không có SSAS), dữ liệu chỉ vài trăm nghìn dòng fact nên SQL trả lời dưới 1 giây, kho luôn "tươi" sau mỗi lần nạp tăng dần (không phải process khối),
  và Power BI (chế độ Import + DAX) đóng vai trò lớp ngữ nghĩa cho người dùng cuối. Đổi lại, với dữ liệu hàng trăm triệu dòng thì ROLAP cần thêm tổng hợp tính sẵn hoặc phân vùng.
"""

OPS = {"010_rollup": "Roll-up", "020_drilldown": "Drill-down", "030_slice": "Slice", "040_dice": "Dice", "050_pivot": "Pivot"}


def split_queries(sql: str) -> tuple[str, list[tuple[str, str]]]:
    head, queries, title, buf = [], [], None, []
    for line in sql.splitlines():
        if line.startswith("-- QUERY:"):
            if title is not None:
                queries.append((title, "\n".join(buf).strip()))
            title, buf = line[len("-- QUERY:"):].strip(), []
        elif title is None:
            head.append(line[2:].strip() if line.startswith("--") else line)
        else:
            buf.append(line)
    if title is not None:
        queries.append((title, "\n".join(buf).strip()))
    return " ".join(h for h in head if h), queries


def md_table(cols: list[str], rows: list[tuple]) -> str:
    def fmt(v):
        if v is None:
            return ""
        if hasattr(v, "quantize"):
            return f"{v:,.2f}"
        return f"{v:,}" if isinstance(v, int) and not isinstance(v, bool) else str(v)
    out = ["| " + " | ".join(cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    out += ["| " + " | ".join(fmt(v) for v in r) + " |" for r in rows]
    return "\n".join(out)


def main() -> None:
    engine = get_engine(config.DB_NAME)
    parts = [f"# Minh hoạ các thao tác OLAP trên kho (ROLAP) – sinh tự động {datetime.now():%Y-%m-%d %H:%M}", "",
             "*Mọi số lấy từ truy vấn thật trên trạng thái cuối của `olist_dw` (đủ dữ liệu). GMV = Σ price của đơn không thuộc nhóm Failed. "
             "File SQL nằm ở `sql/60_olap_examples/`; chạy lại bằng `python scripts/run_olap_examples.py`.*", "", ROLAP_TEXT]
    slow = 0
    with engine.connect() as conn:
        for path in sorted((config.ROOT / "sql" / "60_olap_examples").glob("*.sql")):
            desc, queries = split_queries(path.read_text(encoding="utf-8"))
            parts += [f"## {OPS.get(path.stem, path.stem)} – `{path.name}`", "", desc, ""]
            for title, sql in queries:
                t0 = time.perf_counter()
                res = conn.execute(text(sql))
                cols, rows = list(res.keys()), res.fetchall()
                dt = time.perf_counter() - t0
                slow += dt > 3
                parts += [f"### {title}", "", f"*{len(rows)} dòng, {dt:.2f} giây*", "", md_table(cols, [tuple(r) for r in rows[:30]]), "",
                          "<details><summary>SQL</summary>", "", "```sql", sql, "```", "", "</details>", ""]
                print(f"{path.stem:15s} {dt:5.2f}s {len(rows):>4} rows  {title[:70]}")
    out = config.ROOT / "handoff" / "olap-examples.md"
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"Written {out.relative_to(config.ROOT)}; queries slower than 3 s: {slow}")


if __name__ == "__main__":
    main()
