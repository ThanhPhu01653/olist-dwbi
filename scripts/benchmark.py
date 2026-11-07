"""Compact benchmark (P7-A):  python scripts/benchmark.py

3 analytic queries (GMV by state x month, lead time by state, seller scorecard) + 1 selective lookup measured with EXPLAIN (ANALYZE),
mean of 5 runs after one warm-up, for:
  (1) oltp (normalised joins on the source schema)  vs  dw (star schema, with FK indexes)
  (2) dw with vs without the foreign-key indexes (indexes are dropped inside a transaction that is ROLLED BACK, nothing is changed)
  (3) plain view vs materialized view of the same definition (the materialized copies are temporary objects, also rolled back)
Writes handoff/benchmark.md (tables) and figures/3-5-1_benchmark.png. Run on the final data (olist_dw after all increments).
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from etl import config
from etl.db import get_engine

RUNS = 5
NF = "s.status_group <> 'Failed'"
Q = {
    "Q1 GMV theo bang × tháng": {
        "oltp": "SELECT c.customer_state, to_char(o.order_purchase_timestamp, 'YYYY-MM') AS ym, sum(i.price) AS gmv, count(DISTINCT o.order_id) AS orders "
                "FROM oltp.orders o JOIN oltp.order_items i ON i.order_id = o.order_id JOIN oltp.customers c ON c.customer_id = o.customer_id "
                "WHERE o.order_status NOT IN ('canceled', 'unavailable') GROUP BY 1, 2",
        "dw": "SELECT g.state_code, d.year_month, sum(f.price) AS gmv, count(DISTINCT f.order_id) AS orders FROM dw.fact_order_item f "
              "JOIN dw.dim_date d ON d.date_key = f.purchase_date_key JOIN dw.dim_geography g ON g.geography_key = f.customer_geography_key "
              f"JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND {NF} GROUP BY 1, 2",
        "view": "SELECT * FROM mart_sales.v_sales_state_month",
        "mv_src": "SELECT * FROM mart_sales.v_sales_state_month"},
    "Q2 Lead time theo bang": {
        "oltp": "SELECT c.customer_state, avg(extract(epoch FROM o.order_delivered_customer_date - o.order_purchase_timestamp) / 86400) AS lead_days, count(*) AS orders "
                "FROM oltp.orders o JOIN oltp.customers c ON c.customer_id = o.customer_id "
                "WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL GROUP BY 1",
        "dw": "SELECT g.state_code, avg(o.lead_days) AS lead_days, count(*) AS orders FROM dw.fact_order_fulfillment o "
              "JOIN dw.dim_geography g ON g.geography_key = o.customer_geography_key WHERE o.is_delivered = 1 GROUP BY 1",
        "view": "SELECT * FROM mart_fulfillment.v_fulfillment_state_month",
        "mv_src": "SELECT * FROM mart_fulfillment.v_fulfillment_state_month"},
    "Q3 Scorecard seller": {
        "oltp": "SELECT i.seller_id, count(DISTINCT o.order_id) AS orders, sum(i.price) AS gmv, "
                "avg((o.order_delivered_customer_date > o.order_estimated_delivery_date)::int) AS late_rate, avg(r.review_score) AS avg_review "
                "FROM oltp.order_items i JOIN oltp.orders o ON o.order_id = i.order_id LEFT JOIN oltp.order_reviews r ON r.order_id = o.order_id "
                "WHERE o.order_status NOT IN ('canceled', 'unavailable') GROUP BY 1",
        "dw": "SELECT sl.seller_id, count(DISTINCT f.order_id) AS orders, sum(f.price) AS gmv, avg(o.is_late::numeric) FILTER (WHERE o.is_delivered = 1) AS late_rate, "
              "avg(r.review_score) AS avg_review FROM dw.fact_order_item f JOIN dw.dim_seller sl ON sl.seller_key = f.seller_key "
              f"JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND {NF} JOIN dw.fact_order_fulfillment o ON o.order_id = f.order_id "
              "LEFT JOIN dw.fact_review r ON r.order_id = f.order_id GROUP BY 1",
        "view": "SELECT * FROM pg_temp.scorecard_plain",           # plain view = the same definition as the materialized mart view
        "matview": "SELECT * FROM mart_acquisition.v_seller_scorecard"},
    "Q4 GMV của một seller (tra cứu chọn lọc)": {
        "oltp": "SELECT count(*), sum(i.price) FROM oltp.order_items i JOIN oltp.orders o ON o.order_id = i.order_id WHERE i.seller_id = '{seller}'",
        "dw": "SELECT count(*), sum(f.price) FROM dw.fact_order_item f JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key "
              f"WHERE f.seller_key = {{seller_key}} AND {NF}"},
}


def explain_ms(cur, sql: str) -> float:
    cur.execute("EXPLAIN (ANALYZE, FORMAT JSON) " + sql)
    plan = cur.fetchone()[0]
    plan = plan if isinstance(plan, list) else json.loads(plan)
    return float(plan[0]["Execution Time"])


def timeit(cur, sql: str) -> dict:
    explain_ms(cur, sql)                                  # warm-up (cache), not counted
    t = [explain_ms(cur, sql) for _ in range(RUNS)]
    return {"mean": statistics.mean(t), "min": min(t), "max": max(t)}


def main() -> None:
    engine = get_engine(config.DB_NAME)
    raw = engine.raw_connection()
    res: dict[str, dict[str, dict]] = {k: {} for k in Q}
    try:
        cur = raw.cursor()
        cur.execute("SELECT seller_key, seller_id FROM mart_acquisition.v_seller_scorecard ORDER BY gmv DESC LIMIT 1")
        sk, sid = cur.fetchone()
        raw.commit()
        for name, v in Q.items():
            fmt = {"seller": sid, "seller_key": sk}
            res[name]["oltp"] = timeit(cur, v["oltp"].format(**fmt) if "{seller" in v["oltp"] else v["oltp"])
            res[name]["dw"] = timeit(cur, v["dw"].format(**fmt) if "{seller" in v["dw"] else v["dw"])
        # (2) without FK indexes: dropped in a transaction that is rolled back
        cur.execute("SELECT indexname FROM pg_indexes WHERE schemaname = 'dw' AND (indexname LIKE 'ix_foi_%' OR indexname LIKE 'ix_fof_%' OR indexname LIKE 'ix_fr_%' "
                    "OR indexname LIKE 'ix_fsm_%' OR indexname LIKE 'ix_fp_%')")
        idx = [r[0] for r in cur.fetchall()]
        for i in idx:
            cur.execute(f"DROP INDEX dw.{i}")
        for name, v in Q.items():
            sql = v["dw"].format(seller=sid, seller_key=sk) if "{seller" in v["dw"] else v["dw"]
            res[name]["dw_noidx"] = timeit(cur, sql)
        raw.rollback()
        # (3) plain view vs materialized view (temporary objects, rolled back)
        cur.execute("SELECT definition FROM pg_matviews WHERE schemaname = 'mart_acquisition' AND matviewname = 'v_seller_scorecard'")
        cur.execute("CREATE VIEW pg_temp.scorecard_plain AS " + cur.fetchone()[0].rstrip(";"))
        for name, v in Q.items():
            if "view" not in v:
                continue
            res[name]["view"] = timeit(cur, v["view"])
            if "mv_src" in v:
                cur.execute(f"CREATE MATERIALIZED VIEW pg_temp.mv_{name[:2].lower()} AS {v['mv_src']}")
                cur.execute(f"ANALYZE pg_temp.mv_{name[:2].lower()}")
                res[name]["matview"] = timeit(cur, f"SELECT * FROM pg_temp.mv_{name[:2].lower()}")
            else:
                res[name]["matview"] = timeit(cur, v["matview"])
        raw.rollback()
    finally:
        raw.close()

    lab = {"oltp": "oltp (join chuẩn hoá)", "dw": "dw (star, có index FK)", "dw_noidx": "dw không index FK", "view": "view thường", "matview": "materialized view"}
    lines = ["# Benchmark gọn (P7-A) – sinh tự động", "",
             f"Mỗi ô là trung bình {RUNS} lần chạy `EXPLAIN (ANALYZE)` sau 1 lần chạy nóng (cache), đơn vị **mili giây** (execution time, không tính truyền kết quả). Dữ liệu: trạng thái cuối của `olist_dw` "
             "(112.650 dòng hàng, 99.441 đơn). Máy dev của Phú (laptop), PostgreSQL mặc định.", "", "## 1. oltp (chuẩn hoá) và dw (star schema)", "",
             "| Truy vấn | oltp | dw (có index FK) | dw nhanh hơn |", "| --- | ---: | ---: | ---: |"]
    for n, r in res.items():
        lines.append(f"| {n} | {r['oltp']['mean']:.1f} | {r['dw']['mean']:.1f} | {r['oltp']['mean'] / r['dw']['mean']:.1f}× |")
    lines += ["", "## 2. dw có và không có index trên khoá ngoại", "", "| Truy vấn | Có index FK | Không index FK | Chậm đi |", "| --- | ---: | ---: | ---: |"]
    for n, r in res.items():
        lines.append(f"| {n} | {r['dw']['mean']:.1f} | {r['dw_noidx']['mean']:.1f} | {r['dw_noidx']['mean'] / r['dw']['mean']:.1f}× |")
    lines += ["", "## 3. View thường và materialized view (cùng định nghĩa; Q1, Q2 đọc view mart theo bang × tháng; Q3 là scorecard seller)", "",
              "| Truy vấn | View thường | Materialized view | Nhanh hơn |", "| --- | ---: | ---: | ---: |"]
    for n, r in res.items():
        if "view" in r:
            lines.append(f"| {n} | {r['view']['mean']:.1f} | {r['matview']['mean']:.3f} | {r['view']['mean'] / r['matview']['mean']:,.0f}× |")
    lines += ["", f"Chi tiết (min–max, ms): " + "; ".join(f"{n.split(' ')[0]} {k}: {v['min']:.1f}–{v['max']:.1f}" for n, r in res.items() for k, v in r.items()), ""]
    (config.ROOT / "handoff" / "benchmark.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:40]))

    # figure: 3 panels, log scale
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), dpi=200)
    panels = [("oltp vs dw (star schema)", [("oltp", "#8A94A6"), ("dw", "#1F6FB2")]), ("dw: có và không có index FK", [("dw", "#1F6FB2"), ("dw_noidx", "#F28E2B")]),
              ("view thường vs materialized view", [("view", "#8A94A6"), ("matview", "#2E9E6B")])]
    for ax, (title, series) in zip(axes, panels):
        names = [n for n, r in res.items() if all(k in r for k, _ in series)]
        w = 0.38
        for j, (k, col) in enumerate(series):
            vals = [res[n][k]["mean"] for n in names]
            bars = ax.bar([i + (j - 0.5) * w for i in range(len(names))], vals, w, color=col, label=lab[k])
            for b, v in zip(bars, vals):
                ax.text(b.get_x() + b.get_width() / 2, v * 1.1, f"{v:.0f}" if v >= 10 else f"{v:.1f}" if v >= 0.1 else f"{v:.2f}", ha="center", fontsize=8)
        ax.set_yscale("log")
        ax.set_xticks(range(len(names)), [n.split(" ")[0] for n in names])
        ax.set(title=title, ylabel="ms (thang log)")
        ax.set_ylim(top=ax.get_ylim()[1] * 8)
        ax.legend(fontsize=8, loc="upper right")
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Thời gian thực thi trung bình (5 lần). Q1 GMV bang×tháng · Q2 lead time theo bang · Q3 scorecard seller · Q4 tra cứu một seller", fontsize=9)
    fig.tight_layout()
    fig.savefig(config.ROOT / "figures" / "3-5-1_benchmark.png")
    print("figure written")


if __name__ == "__main__":
    main()
