"""P8-D5: source data dictionary (11 tables of oltp and crm): type, value domain, % null, role in the warehouse
-> huong-dan/06-tu-dien-du-lieu-nguon.md (+ summary section in handoff/2026-11-14-P8-eda.md).
Role in the DW comes from docs/mapping.csv (source -> ods -> dw); domain and null share come from olist_full.
"""
from __future__ import annotations

import re

from p8_common import *  # noqa: F401,F403

OUT = ROOT / "huong-dan" / "06-tu-dien-du-lieu-nguon.md"
m = pd.read_csv(ROOT / "docs" / "mapping.csv", encoding="utf-8-sig")
a, b = m[m.layer == "nguồn → ods"], m[m.layer == "ods → dw"]

ods_target = {}  # (src table, src col) -> (ods table, ods col)
for r in a.itertuples():
    ods_target[(r.source_table, r.source_column)] = (r.target_table, r.target_column)


def dw_targets(ods_tab: str, ods_col: str) -> list[str]:
    out = []
    for r in b.itertuples():
        if ods_tab in str(r.source_table) and ods_col in [c.strip() for c in re.split(r"[,/]", str(r.source_column))]:
            out.append(r.target_table.replace("dw.", "") + "." + str(r.target_column).split(" / ")[0])
    return sorted(set(out))


cols = q("""SELECT table_schema AS s, table_name AS t, column_name AS c, data_type AS ty, ordinal_position AS pos FROM information_schema.columns
            WHERE table_schema IN ('oltp','crm') ORDER BY table_schema, table_name, ordinal_position""")
TYPE_VN = {"character": "char", "text": "text", "integer": "int", "smallint": "smallint", "bigint": "bigint", "numeric": "numeric", "double precision": "double",
           "timestamp without time zone": "timestamp", "date": "date", "boolean": "boolean"}
KEYS = {("oltp.order_items", "product_id"): "khoá tra cứu dim_product", ("oltp.product_category_name_translation", "product_category_name"): "khoá tra bản dịch danh mục (dim_product)"}
KEYS.update({("crm.closed_deals", c): "dim_lead_profile (junk dimension, 7 thuộc tính)" for c in ["lead_type", "lead_behaviour_profile", "has_company", "has_gtin", "average_stock"]})
lines = ["# 06 – Từ điển dữ liệu nguồn (11 bảng oltp và crm)", "",
         "> Sinh tự động bởi `python scripts/eda/p8_dictionary.py` trên database `olist_full`; mapping lấy từ `docs/mapping.csv`. Từ điển các bảng của kho (`dw`, `mart_*`) nằm ở [`03-tu-dien-du-lieu.md`](03-tu-dien-du-lieu.md).", "",
         "Cột *Miền giá trị*: khoảng min–max với cột số và ngày; với cột chữ là số giá trị phân biệt và, nếu ít, danh sách giá trị. *% rỗng* là tỷ lệ NULL hoặc chuỗi rỗng. *Vai trò trong DW* là cột đích của dimension hoặc fact; \"không dùng\" nghĩa là cột không đi sang kho.", ""]
summary = []
for (s, t), g in cols.groupby(["s", "t"], sort=False):
    full = f"{s}.{t}"
    total = scalar(f'SELECT count(*) FROM "{s}"."{t}"')
    lines += [f"## `{full}` ({n(total)} dòng, {len(g)} cột)", "", "| Cột | Kiểu | Miền giá trị | % rỗng | Vai trò trong DW |", "| --- | --- | --- | ---: | --- |"]
    for r in g.itertuples():
        c = r.c
        isnum = r.ty in ("integer", "smallint", "bigint", "numeric", "double precision")
        isdt = r.ty in ("date", "timestamp without time zone")
        nulls = scalar(f'SELECT count(*) FILTER (WHERE "{c}" IS NULL OR "{c}"::text = \'\') FROM "{s}"."{t}"')
        dist = scalar(f'SELECT count(DISTINCT "{c}") FROM "{s}"."{t}"')
        if isnum or isdt:
            mn, mx = q(f'SELECT min("{c}")::text AS a, max("{c}")::text AS b FROM "{s}"."{t}"').iloc[0]
            dom = f"{mn} … {mx}" if r.ty not in ("timestamp without time zone",) else f"{str(mn)[:10]} … {str(mx)[:10]}"
            if r.ty == "double precision" or r.ty == "numeric":
                try:
                    dom = f"{float(mn):.4g} … {float(mx):.6g}"
                except Exception:
                    pass
        elif dist <= 12:
            vals = q(f'SELECT "{c}"::text AS v, count(*) AS k FROM "{s}"."{t}" GROUP BY 1 ORDER BY 2 DESC LIMIT 12')
            dom = "; ".join(str(v) for v in vals["v"].tolist())
            dom = f"{dist} giá trị: {dom}"
        else:
            ex = scalar(f'SELECT "{c}"::text FROM "{s}"."{t}" WHERE "{c}" IS NOT NULL LIMIT 1')
            dom = f"{n(dist)} giá trị phân biệt (ví dụ {str(ex)[:14]}{'…' if len(str(ex)) > 14 else ''})"
        role = []
        tgt = ods_target.get((full, c))
        if tgt:
            role = dw_targets(*tgt)
        if (full, c) in KEYS:
            role = role + [KEYS[(full, c)]]
        if (full, c) in (("crm.closed_deals", "business_segment"), ("crm.closed_deals", "business_type")):
            role = role + ["dim_lead_profile (junk dimension, 7 thuộc tính)"]
        role_txt = ", ".join(role[:5]) + (" …" if len(role) > 5 else "") if role else "không dùng"
        lines.append(f"| `{c}` | {TYPE_VN.get(r.ty, r.ty)} | {dom.replace('|', '/')} | {n(100 * nulls / total, 1)}% | {role_txt} |")
        summary.append((full, c, nulls / total, bool(role)))
    lines.append("")
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("written:", OUT.relative_to(ROOT))
sdf = pd.DataFrame(summary, columns=["t", "c", "null", "used"])
high = sdf[sdf["null"] > 0.05].sort_values("null", ascending=False)
section("dictionary", [
    f"Từ điển 11 bảng nguồn (71 cột) nằm ở `huong-dan/06-tu-dien-du-lieu-nguon.md`: kiểu, miền giá trị, % rỗng và vai trò trong kho của từng cột.", "",
    f"- {int((sdf['null'] > 0).sum())} trong {len(sdf)} cột có giá trị rỗng; {len(high)} cột rỗng trên 5%: " + ", ".join(f"`{r.t.split('.')[1]}.{r.c}` ({n(100 * r.null, 1)}%)" for r in high.itertuples()) + ".",
    f"- {int(sdf['used'].sum())} cột có vai trò rõ trong kho theo bảng mapping; các cột còn lại ghi \"không dùng\" (xem cột *Vai trò trong DW*).", ""])
