"""P1 step 1: profile every source table -> handoff/profiling.md + figures/3-3-1_null_heatmap.png.

For each column: type, % null, distinct values, min/max (numbers, dates) or length range (text), top values.
"""
from __future__ import annotations

from common import *  # noqa: F401,F403

TABLES = [
    "oltp.orders", "oltp.order_items", "oltp.order_payments", "oltp.order_reviews", "oltp.customers",
    "oltp.sellers", "oltp.products", "oltp.geolocation", "oltp.product_category_name_translation",
    "crm.mql", "crm.closed_deals",
]
NUMERIC = {"integer", "smallint", "bigint", "numeric", "double precision"}
TEMPORAL = {"timestamp without time zone", "date"}


def type_label(row) -> str:
    if row.data_type == "character":
        return f"char({int(row.character_maximum_length)})"
    if row.data_type == "numeric":
        return f"numeric({int(row.numeric_precision)},{int(row.numeric_scale)})"
    return {"timestamp without time zone": "timestamp", "double precision": "double"}.get(row.data_type, row.data_type)


def profile_table(table: str) -> tuple[pd.DataFrame, int]:
    schema, name = table.split(".")
    cols = q("SELECT column_name, data_type, character_maximum_length, numeric_precision, numeric_scale "
             "FROM information_schema.columns WHERE table_schema = :s AND table_name = :t ORDER BY ordinal_position",
             s=schema, t=name)
    total = int(scalar(f"SELECT count(*) FROM {table}"))
    rows = []
    for c in cols.itertuples():
        col = c.column_name
        s = q(f'SELECT count(*) FILTER (WHERE "{col}" IS NULL) AS nulls, count(DISTINCT "{col}") AS dist FROM {table}').iloc[0]
        nulls, dist = int(s.nulls), int(s.dist)
        rng = "–"
        if c.data_type in NUMERIC | TEMPORAL:
            r = q(f'SELECT min("{col}")::text AS lo, max("{col}")::text AS hi FROM {table}').iloc[0]
            rng = f"{r.lo} … {r.hi}"
        elif c.data_type in ("text", "character") and dist > 1 and c.data_type == "text":
            r = q(f'SELECT min(length("{col}")) AS lo, max(length("{col}")) AS hi FROM {table}').iloc[0]
            rng = f"độ dài {int(r.lo)}–{int(r.hi)}"
        top = "–"
        low_cardinality = 0 < dist <= 1000 and dist < 0.5 * max(total - nulls, 1)
        if low_cardinality or c.data_type == "boolean":
            t = q(f'SELECT "{col}"::text AS v, count(*) AS c FROM {table} WHERE "{col}" IS NOT NULL GROUP BY 1 ORDER BY 2 DESC, 1 LIMIT 3')
            top = "; ".join(f"{str(v)[:28]} ({n(int(k))})" for v, k in zip(t.v, t.c))
        rows.append({"Cột": col, "Kiểu": type_label(c), "% null": pct(100 * nulls / total if total else 0, 2),
                     "Số giá trị khác nhau": n(dist), "Min … Max": rng, "Top giá trị (số lần)": top,
                     "_null_pct": 100 * nulls / total if total else 0.0, "_nulls": nulls})
    return pd.DataFrame(rows), total


def wrap_name(col: str, width: int = 17) -> str:
    """Wrap a snake_case name at underscores (never inside a word)."""
    parts, lines, cur = col.split("_"), [], ""
    for i, w in enumerate(parts):
        w = w + ("_" if i < len(parts) - 1 else "")
        if cur and len(cur) + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur += w
    lines.append(cur)
    return chr(10).join(lines)


def null_label(v: float) -> str:
    return pct(v, 2) if 0 < v < 0.1 else pct(v, 1)


def null_heatmap(profiles: dict[str, pd.DataFrame]) -> str:
    max_cols = max(len(p) for p in profiles.values())
    names = [t.split(".")[1].replace("product_category_name_translation", "category_translation") for t in profiles]
    grid = np.full((len(profiles), max_cols), np.nan)
    labels = [[""] * max_cols for _ in profiles]
    for i, p in enumerate(profiles.values()):
        for j, (col, pc) in enumerate(zip(p["Cột"], p["_null_pct"])):
            grid[i, j] = pc
            labels[i][j] = wrap_name(col)
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("blues", ["#f0f6fd", "#9ec5f4", "#3987e5", "#184f95", "#0d366b"])
    fig, ax = plt.subplots(figsize=(18, 7.4))
    ax.grid(False)
    masked = np.ma.masked_invalid(grid)
    im = ax.imshow(masked, cmap=cmap, vmin=0, vmax=100, aspect="auto")
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            if np.isnan(grid[i, j]):
                continue
            dark = grid[i, j] > 35
            ax.text(j, i - 0.12, labels[i][j], ha="center", va="center", fontsize=6.3,
                    color="white" if dark else INK2)
            ax.text(j, i + 0.30, null_label(grid[i, j]), ha="center", va="center", fontsize=7.5, fontweight="bold",
                    color="white" if dark else INK)
    ax.set_yticks(range(len(names)), names, fontsize=9, color=INK)
    ax.set_xticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("Tỷ lệ giá trị rỗng (NULL) của từng cột trong các bảng nguồn")
    cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.01)
    cb.set_label("% giá trị rỗng", color=INK2)
    cb.outline.set_visible(False)
    return save(fig, "3-3-1_null_heatmap")


def main() -> None:
    lines = ["# Profiling dữ liệu nguồn (olist_full)", "",
             source_note("profile.py"), "",
             "Mỗi bảng: số dòng, số cột, và với từng cột: kiểu dữ liệu, % giá trị rỗng (NULL), số giá trị khác nhau, "
             "giá trị nhỏ nhất/lớn nhất (cột số, ngày) hoặc độ dài chuỗi (cột văn bản), 3 giá trị phổ biến nhất "
             "(chỉ hiển thị với cột có ít giá trị khác nhau).", ""]
    summary, profiles = [], {}
    for t in TABLES:
        p, total = profile_table(t)
        profiles[t] = p
        with_null = p[p["_nulls"] > 0]
        summary.append({"Bảng": t, "Số dòng": n(total), "Số cột": len(p),
                        "Cột có NULL": ", ".join(f"{c} ({pct(v, 2)})" for c, v in zip(with_null["Cột"], with_null["_null_pct"])) or "không có"})
        lines += [f"## {t}", "", f"{n(total)} dòng × {len(p)} cột.", "",
                  md_table(p.drop(columns=["_null_pct", "_nulls"]), ["% null", "Số giá trị khác nhau"]), ""]
    fig = null_heatmap(profiles)
    head = ["## Tóm tắt", "", md_table(pd.DataFrame(summary), ["Số dòng", "Số cột"]), "",
            f"Hình: `{fig}` – bản đồ nhiệt tỷ lệ NULL của mọi cột (ô trống = bảng không có cột đó).", ""]
    lines = lines[:6] + head + lines[6:]
    write_md("profiling.md", lines)


if __name__ == "__main__":
    main()
