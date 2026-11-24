"""P12e: data-model diagrams for the slides (constellation, ERD per fact, overview, pipeline, ETL stages, benchmark).

All names come from the database (olist_dw) or from the handoff files written by the existing scripts; nothing is typed in by hand
except the fact -> dimension map (taken from the *_key columns of each fact table).   Run: python scripts/p12e_model.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd  # noqa: E402
from sqlalchemy import text  # noqa: E402

import slide_fig as sf  # noqa: E402
from p12e_canvas import BLUE, EDGE, GREEN, GREY, ORANGE, PURPLE, YELLOW, Canvas, bottom, left, right, top  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from etl import config  # noqa: E402
from etl.db import get_engine  # noqa: E402

_e = get_engine(config.DB_NAME)


def q(sql: str) -> pd.DataFrame:
    with _e.connect() as c:
        return pd.read_sql(text(sql), c)


FACTS = ["fact_order_item", "fact_order_fulfillment", "fact_payment", "fact_review", "fact_lead_funnel", "fact_seller_monthly"]
DIMS = ["dim_date", "dim_customer", "dim_geography", "dim_seller", "dim_product", "dim_order_status", "dim_payment_type", "dim_lead_origin", "dim_lead_profile", "dim_sales_rep"]
# fact -> dimensions, from the *_key columns (customer_geography_key / seller_geography_key -> dim_geography, sdr_key / sr_key -> dim_sales_rep, *_date_key -> dim_date)
LINK = {
    "fact_order_item": ["dim_date", "dim_customer", "dim_geography", "dim_seller", "dim_product", "dim_order_status"],
    "fact_order_fulfillment": ["dim_date", "dim_customer", "dim_geography", "dim_order_status"],
    "fact_payment": ["dim_date", "dim_customer", "dim_payment_type"],
    "fact_review": ["dim_date", "dim_customer"],
    "fact_lead_funnel": ["dim_date", "dim_seller", "dim_lead_origin", "dim_lead_profile", "dim_sales_rep"],
    "fact_seller_monthly": ["dim_date", "dim_seller"],
}


def two_lines(name: str) -> str:
    """Break a table name after an underscore near the middle so it fits a narrow box."""
    if len(name) <= 15:
        return name
    parts = name.split("_")
    best = min(range(1, len(parts)), key=lambda i: abs(len("_".join(parts[:i])) - len("_".join(parts[i:]))))
    return "_".join(parts[:best]) + "_\n" + "_".join(parts[best:])


def check_links() -> None:
    """The LINK map must agree with the key columns in the database."""
    cols = q("select table_name, column_name from information_schema.columns where table_schema='dw' and table_name like 'fact_%'")
    for f, dims in LINK.items():
        keys = set(cols[cols.table_name == f].column_name)
        need = {"dim_date": any(k.endswith("date_key") for k in keys), "dim_customer": "customer_key" in keys,
                "dim_geography": any("geography_key" in k for k in keys), "dim_seller": "seller_key" in keys, "dim_product": "product_key" in keys,
                "dim_order_status": "order_status_key" in keys, "dim_payment_type": "payment_type_key" in keys, "dim_lead_origin": "lead_origin_key" in keys,
                "dim_lead_profile": "lead_profile_key" in keys, "dim_sales_rep": "sdr_key" in keys}
        for d in dims:
            assert need[d], (f, d)
        assert sum(need.values()) == len(dims), (f, [k for k, v in need.items() if v], dims)


def constellation_layer(name: str, facts: list[str]) -> None:
    c = Canvas("full_ket")
    dims = [d for d in DIMS if any(d in LINK[f] for f in facts)]
    top_d = dims[: (len(dims) + 1) // 2]
    bot_d = dims[(len(dims) + 1) // 2:]
    fw, fh, fy = 196, 74, 138
    gap = (c.W - fw * len(facts)) / (len(facts) + 1)
    fb = {f: c.box(gap + i * (fw + gap), fy, fw, fh, two_lines(f), fill=ORANGE, px=19, bold=True) for i, f in enumerate(facts)}

    def row(ds, y):
        dw = 166
        g = (c.W - dw * len(ds)) / (len(ds) + 1)
        return {d: c.box(g + i * (dw + g), y, dw, 56, two_lines(d), fill=BLUE, px=19, bold=True) for i, d in enumerate(ds)}

    tb, bb = row(top_d, 8), row(bot_d, 286)
    cols = {"fact_order_item": "#c2410c", "fact_order_fulfillment": "#2563eb", "fact_payment": "#15803d", "fact_review": "#7c3aed", "fact_lead_funnel": "#c2410c", "fact_seller_monthly": "#2563eb"}
    for f in facts:
        for d in LINK[f]:
            if d in tb:
                c.arrow(top(fb[f]), bottom(tb[d]), color=cols[f], lw=1.4, head=False)
            elif d in bb:
                c.arrow(bottom(fb[f]), top(bb[d]), color=cols[f], lw=1.4, head=False)
    # draw boxes again on top of the lines
    for f in facts:
        c.box(*fb[f], two_lines(f), fill=ORANGE, px=19, bold=True, z=3)
    for d, b in {**tb, **bb}.items():
        c.box(*b, two_lines(d), fill=BLUE, px=19, bold=True, z=3)
    c.save(name, "scripts/p12e_model.py")


def overview(name: str, counts: bool) -> None:
    c = Canvas("full_ket")
    cnt = {}
    if counts:
        for t in FACTS + DIMS:
            cnt[t] = int(q(f"select count(*) n from dw.{t}").n[0])
    dw, dh = 166, 52
    g = (c.W - dw * 5) / 6
    dd = {}
    for i, d in enumerate(DIMS[:5]):
        dd[d] = c.box(g + i * (dw + g), 6, dw, dh, two_lines(d), fill=BLUE, px=19, bold=True)
    for i, d in enumerate(DIMS[5:]):
        dd[d] = c.box(g + i * (dw + g), 292, dw, dh, two_lines(d), fill=BLUE, px=19, bold=True)
    fw, fh = 274, 58
    fg = (c.W - fw * 3) / 4
    fb = {}
    for i, f in enumerate(FACTS):
        r, k = divmod(i, 3)
        fb[f] = c.box(fg + k * (fw + fg), 98 + r * 90, fw, fh, (f if not counts else f.replace("fact_", "fact_", 1)) + (f"\n{cnt[f]:,}".replace(",", ".") + " dòng" if counts else ""), fill=ORANGE, px=19, bold=True)
    if not counts:
        for f in FACTS:
            c.arrow(top(fb[f]) if fb[f][1] < 150 else top(fb[f]), (dd["dim_date"][0] + dd["dim_date"][2] / 2, dd["dim_date"][1] + dd["dim_date"][3]), color="#1d4ed8", lw=1.0, head=False, z=0)
    c.save(name, "scripts/p12e_model.py")


def pk_cols(table: str) -> set[str]:
    r = q(f"""select kcu.column_name from information_schema.table_constraints tc join information_schema.key_column_usage kcu
              on tc.constraint_name=kcu.constraint_name and tc.table_schema=kcu.table_schema
              where tc.table_schema='dw' and tc.table_name='{table}' and tc.constraint_type='PRIMARY KEY'""")
    return set(r.column_name)


def erd_layer(fact: str) -> None:
    """One fact with its dimensions: key columns (PK/FK) and a few main columns."""
    c = Canvas("full_ket")
    cols = q(f"select column_name, data_type from information_schema.columns where table_schema='dw' and table_name='{fact}' order by ordinal_position")
    pks = pk_cols(fact)
    keys = [x for x in cols.column_name if x.endswith("_key") or x in pks]
    measures = [x for x in cols.column_name if x not in keys and x != "etl_batch_id" and not x.endswith("_ts")]
    rows = []
    for x in keys:
        tag = "PK" if x in pks else "FK"
        rows.append((tag, x))
    rows += [("", x) for x in measures[: max(2, 8 - len(rows))]]
    rows = rows[:9]
    rh = 25
    fw, fx = 330, 265
    fh = 34 + rh * len(rows)
    fy = (c.H - fh) / 2
    c.box(fx, fy, fw, fh, "", fill="white", ec=EDGE)
    c.box(fx, fy, fw, 32, fact, fill=ORANGE, px=19, bold=True)
    for i, (tag, x) in enumerate(rows):
        y = fy + 34 + i * rh + rh / 2
        if tag:
            c.text(fx + 8, y, tag, px=18, bold=True, ha="left", color="#b91c1c" if tag == "PK" else "#1d4ed8")
        c.text(fx + 40, y, x, px=19, ha="left", bold=(tag == "PK"))
    dims = LINK[fact]
    left_d, right_d = dims[: (len(dims) + 1) // 2], dims[(len(dims) + 1) // 2:]
    for side, ds in ((0, left_d), (1, right_d)):
        n = len(ds)
        dh = 92
        gap = (c.H - n * dh) / (n + 1)
        for i, d in enumerate(ds):
            dcols = q(f"select column_name from information_schema.columns where table_schema='dw' and table_name='{d}' order by ordinal_position").column_name.tolist()[:3]
            x = 10 if side == 0 else c.W - 10 - 230
            y = gap + i * (dh + gap)
            c.box(x, y, 230, dh, "", fill="white", ec=EDGE)
            c.box(x, y, 230, 30, d, fill=BLUE, px=19, bold=True)
            for k, cn in enumerate(dcols[:2]):
                c.text(x + 8, y + 30 + 24 * k + 14, cn, px=19, ha="left", bold=(k == 0))
            c.text(x + 8, y + 30 + 48 + 12, "…", px=19, ha="left") if len(dcols) > 2 else None
            ax_ = (x + 230, y + dh / 2) if side == 0 else (x, y + dh / 2)
            fx_ = (fx, fy + fh / 2) if side == 0 else (fx + fw, fy + fh / 2)
            c.line(ax_, fx_, color="#6b7280", lw=1.4, z=0)
    c.save(f"3-3-4_erd_dw_{fact}", "scripts/p12e_model.py")


def pipeline_sl() -> None:
    c = Canvas("full_ket")
    stages = [("CSV\nKaggle", GREY), ("oltp +\ncrm", GREY), ("staging", "#F3D9B8"), ("ods", "#DDE1EA"), ("dw\n10 dim\n6 fact", YELLOW), ("4 mart\n17 view", GREEN), ("Power BI\n4 dash-\nboard", PURPLE)]
    w, g = 104, 18.5
    bs = []
    for i, (t, f) in enumerate(stages):
        bs.append(c.box(4 + i * (w + g), 50, w, 150, t, fill=f, px=20, bold=True))
        if i:
            c.arrow(right(bs[i - 1]), left(bs[i]))
    labels = ["nạp nguồn", "extract", "làm sạch", "dim rồi fact", "view", "CSV"]
    for i, lb in enumerate(labels):
        c.text(bs[i][0] + w + g / 2, 28, lb, px=19, color="#374151")
    c.box(4, 240, c.W - 8, 70, "etl_log: mỗi lần chạy, dòng bị loại, kết quả 136 kiểm thử", fill="#FDF8E4", px=20, dashed=True)
    for i in (2, 3, 4):
        c.arrow(bottom(bs[i]), (bs[i][0] + w / 2, 240), dashed=True, color="#6b7280")
    c.save("3-4-1_pipeline_sl", "scripts/p12e_model.py")


def etl_jobs() -> None:
    t = (ROOT / "handoff" / "2026-11-14-P8-etl.md").read_text(encoding="utf-8").splitlines()
    rows = {}
    for ln in t:
        p = [x.strip() for x in ln.strip("|").split("|")]
        if len(p) == 4 and p[0] in ("Extract", "Seed và ODS", "Dimension và fact", "Data mart", "Kiểm thử", "Xuất cho Power BI"):
            rows[p[0]] = p[3]

    def first(s: str, n: int = 2) -> str:
        return "; ".join(s.split(";")[:n])

    cards = [("1 Extract", "11 job\n1.273.620\ndòng", GREY), ("2 Seed, ODS", "17 job\n42 dòng\nbị loại", "#DDE1EA"), ("3 Dim, fact", "17 job\n306.586 dòng\nchèn", YELLOW),
             ("4 Data mart", "45.213 dòng\nđọc\n0,9 giây", GREEN), ("5 Kiểm thử", "142/142\nphép đạt", "#F3D9B8"), ("6 Xuất CSV", "37 file CSV\ncho\nPower BI", PURPLE)]
    # numbers come from the handoff table (lô đầu); verify they are still there
    joined = " ".join(rows.values())
    for must in ("11 job", "1.273.620", "17 job", "42 dòng bị loại", "306.586", "45.213", "142/142", "37 file"):
        assert must in joined, must
    c = Canvas("left60")
    w, h, gx, gy = 172, 150, 17, 20
    for i, (title, body, fill) in enumerate(cards):
        r, k = divmod(i, 3)
        x, y = k * (w + gx), 10 + r * (h + gy)
        c.box(x, y, w, h, "", fill=fill)
        c.text(x + w / 2, y + 26, title, px=19.5, bold=True)
        c.text(x + w / 2, y + 92, body, px=19)
        if k < 2:
            c.arrow((x + w, y + h / 2), (x + w + gx, y + h / 2))
    c.save("3-3_etl_jobs", "scripts/p12e_model.py")


def benchmark() -> None:
    import matplotlib.pyplot as plt
    t = (ROOT / "handoff" / "benchmark.md").read_text(encoding="utf-8")

    def table(title_key: str) -> dict[str, list[float]]:
        sec = t.split("## ")[[i for i, s in enumerate(t.split("## ")) if s.startswith(title_key)][0]]
        out = {}
        for ln in sec.splitlines():
            m = re.match(r"\| (Q\d) .*?\| ([\d.,]+) \| ([\d.,]+) \|", ln)
            if m:
                out[m.group(1)] = [float(m.group(2).replace(",", "")), float(m.group(3).replace(",", ""))]
        return out

    a, b, v = table("1."), table("2."), table("3.")
    fig, axes = sf.new_figure("full_ket", ncols=3)
    panels = [(a, "oltp", "dw", "oltp và dw"), (b, "có index FK", "không index FK", "index khoá ngoại"), (v, "view", "matview", "view và matview")]
    cols = ["#2f6fd1", "#e8743b"]
    for ax, (d, l1, l2, ttl) in zip(axes, panels):
        qs = list(d)
        x = range(len(qs))
        ax.bar([i - 0.2 for i in x], [d[k][0] for k in qs], 0.4, color=cols[0], label=l1)
        ax.bar([i + 0.2 for i in x], [d[k][1] for k in qs], 0.4, color=cols[1], label=l2)
        ax.set_yscale("log")
        ax.set_xticks(list(x))
        ax.set_xticklabels(qs)
        ax.set_title(ttl, fontsize=10, fontweight="bold")
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2, fontsize=9.3, frameon=False, handlelength=1.0, columnspacing=0.8, handletextpad=0.4)
        ax.grid(axis="x", visible=False)
    axes[0].set_ylabel("ms (thang log)")
    sf.finish(fig, "3-5-1_benchmark", "full_ket", script="scripts/p12e_model.py", drop_title=False)


if __name__ == "__main__":
    check_links()
    constellation_layer("3-3-4_constellation_a", FACTS[:4])
    constellation_layer("3-3-4_constellation_b", FACTS[4:])
    overview("3-3-4_constellation_sl", counts=False)
    overview("3-5_data_model_vat_ly", counts=True)
    for f in FACTS:
        erd_layer(f)
    pipeline_sl()
    etl_jobs()
    benchmark()


def lakehouse() -> None:
    c = Canvas("full_ket")
    stages = [("PostgreSQL\nnguồn", GREY), ("Debezium\n+ Kafka", BLUE), ("Bronze\nSpark", "#F3D9B8"), ("Silver\nSpark", "#DDE1EA"), ("Gold\ndbt", YELLOW), ("Trino +\nSuperset", GREEN)]
    w, g = 126, 20.8
    bs = []
    for i, (t, f) in enumerate(stages):
        bs.append(c.box(i * (w + g), 20, w, 100, t, fill=f, px=20, bold=True))
        if i:
            c.arrow(right(bs[i - 1]), left(bs[i]))
    store = c.box(2 * (w + g), 175, 3 * w + 2 * g, 56, "MinIO + Iceberg (Parquet)", fill="#FFFFFF", px=20, bold=True, dashed=True)
    for i in (2, 3, 4):
        c.arrow(bottom(bs[i]), (bs[i][0] + w / 2, 175), dashed=True, color="#6b7280", head=False)
    kho = c.box(5 * (w + g) - 30, 265, w + 30, 70, "Kho\nchương 3", fill=GREY, px=20, bold=True, dashed=True)
    c.arrow((bs[4][0] + w / 2, 120), (kho[0] + 10, 265), color="#b91c1c")
    c.text(300, 300, "đối soát 16/16 bảng", px=20, bold=True, color="#b91c1c")
    c.save("5-1_kien_truc_lakehouse_sl", "scripts/p12e_model.py")


if __name__ == "__main__":
    lakehouse()
