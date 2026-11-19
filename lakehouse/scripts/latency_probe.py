"""End-to-end latency and burst throughput of the running stream (Step 9).

    python lakehouse/scripts/latency_probe.py [--probes 6] [--burst 20000] [--md handoff/2026-11-19-P10-latency.md] [--png figures/5-1_latency.png]

The Spark stream (stream_bronze_silver.py, trigger 30 s) must be running. A probe = one UPDATE of the estimated delivery date of one order in the source PostgreSQL
(committed), then the time until the change is (a) in Kafka (Kafka record timestamp), (b) in Bronze (ingested_at), (c) written to Silver (processed_at) and (d) readable
through Trino. All timestamps come from containers of the same VM (PostgreSQL clock, Kafka, Spark, Trino), so they are comparable. Every change is reverted at the end;
the source returns to its previous content, so Silver = source and Gold = warehouse still hold.
The burst updates N orders in one transaction to measure how fast the stream drains a backlog.
"""
from __future__ import annotations

import argparse
import random
import statistics
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psycopg2
from trino.dbapi import connect

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lh_env import ROOT, load_env  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--probes", type=int, default=6)
ap.add_argument("--burst", type=int, default=20000)
ap.add_argument("--timeout", type=int, default=150, help="seconds to wait for one probe before giving up")
ap.add_argument("--md")
ap.add_argument("--png")
a = ap.parse_args()

env = load_env()
pg = psycopg2.connect(host="127.0.0.1", port=int(env["LH_PG_PORT"]), user=env["LH_PG_USER"], password=env["LH_PG_PASSWORD"], dbname=env["LH_PG_DB"])
pg.autocommit = False
tr = connect(host="127.0.0.1", port=int(env["LH_TRINO_PORT"]), user="latency_probe", catalog="iceberg", schema="silver")
LINES: list[str] = []


def out(t=""):
    print(t, flush=True)
    LINES.append(t)


def trq(sql):
    c = tr.cursor()
    c.execute(sql)
    return c.fetchall()


def pg_now():
    with pg.cursor() as c:
        c.execute("select extract(epoch from clock_timestamp())")
        return float(c.fetchone()[0])


def run_update(sql, params=()):
    with pg.cursor() as c:
        c.execute(sql, params)
    pg.commit()
    return pg_now()


def ts(v):
    return v.astimezone(timezone.utc).timestamp()


# ------------------------------------------------------------------ probes
with pg.cursor() as c:
    c.execute("select order_id, to_char(order_estimated_delivery_date, 'YYYY-MM-DD HH24:MI:SS') from oltp.orders order by order_id desc limit 1")
    oid, base = c.fetchone()
oid = oid.strip()
out(f"Đơn thử: `{oid}`, ngày giao dự kiến gốc {base}. Mỗi lần thử cộng thêm i ngày, cuối cùng trả về giá trị gốc.")
rows = []
rng = random.Random(7)
for i in range(1, a.probes + 1):
    time.sleep(rng.uniform(2, 20))                              # random phase against the 30 s trigger
    t0 = run_update("update oltp.orders set order_estimated_delivery_date = %s::timestamp + (%s * interval '1 day') where order_id = %s", (base, i, oid))
    seen = None
    deadline = time.time() + a.timeout
    nxt = time.time() + 30
    while time.time() < deadline:
        r = trq(f"select order_estimated_delivery_date, processed_at, to_unixtime(current_timestamp) from orders where order_id = '{oid}'")[0]
        if r[0].date() == (datetime.fromisoformat(base) + timedelta(days=i)).date():
            seen = (r[1], float(r[2]))
            break
        if time.time() > nxt:
            print(f"  probe {i}: waiting {time.time() - t0:.0f} s ...", flush=True)
            nxt += 30
        time.sleep(1)
    if seen is None:
        out(f"- probe {i}: **không thấy trong Silver sau {a.timeout} giây** (dừng chờ)")
        continue
    b = trq(f"select kafka_timestamp, ingested_at from bronze.oltp_orders where key like '%{oid}%' order by kafka_offset desc limit 1")[0]
    kafka, bronze, silver = ts(b[0]), ts(b[1]), ts(seen[0])
    rows.append(dict(i=i, pg_kafka=kafka - t0, kafka_bronze=bronze - kafka, bronze_silver=silver - bronze, e2e_written=silver - t0, e2e_visible=seen[1] - t0))
    out(f"- probe {i}: PostgreSQL → Kafka {rows[-1]['pg_kafka']:.2f} s; Kafka → Bronze {rows[-1]['kafka_bronze']:.1f} s; Bronze → Silver {rows[-1]['bronze_silver']:.1f} s; "
        f"tổng đến lúc Silver ghi xong {rows[-1]['e2e_written']:.1f} s, đến lúc đọc được qua Trino {rows[-1]['e2e_visible']:.1f} s")
run_update("update oltp.orders set order_estimated_delivery_date = %s::timestamp where order_id = %s", (base, oid))
out()
if rows:
    out("| Chặng (giây) | nhỏ nhất | trung bình | lớn nhất |")
    out("| --- | ---: | ---: | ---: |")
    for k, name in (("pg_kafka", "PostgreSQL → Kafka (Debezium)"), ("kafka_bronze", "Kafka → Bronze"), ("bronze_silver", "Bronze → Silver"), ("e2e_written", "**Tổng: nguồn → Silver ghi xong**"),
                    ("e2e_visible", "Tổng: nguồn → đọc được qua Trino")):
        v = [r[k] for r in rows]
        out(f"| {name} | {min(v):.1f} | {statistics.mean(v):.1f} | {max(v):.1f} |")
    out(f"\n{len(rows)} lần thử, trigger 30 giây. Chặng "Kafka → Bronze" gồm thời gian chờ đến lần kích hoạt kế tiếp của micro-batch (0 đến 30 giây, trung bình kỳ vọng 15 giây); chặng "Bronze → Silver" là thời gian xử lý của lô (MERGE vào Iceberg). Chặng PostgreSQL → Kafka (Debezium) dưới 1 giây.")

# ------------------------------------------------------------------ burst
burst = None
if a.burst:
    out(f"\n## Thông lượng khi dồn việc: cập nhật {a.burst:,} đơn trong một giao dịch".replace(",", "."))
    t0 = run_update("update oltp.orders set order_estimated_delivery_date = order_estimated_delivery_date + interval '1 day' where order_id in (select order_id from oltp.orders where order_id <> %s order by order_id limit %s)", (oid, a.burst))
    t0ms = int(t0 * 1000)
    deadline = time.time() + 540
    nxt = time.time() + 60
    done = None
    while time.time() < deadline:
        n = trq(f"select count(*) from orders where src_ts_ms >= {t0ms}")[0][0]
        if n >= a.burst:
            done = time.time() - t0
            break
        if time.time() > nxt:
            print(f"  burst: {n:,}/{a.burst:,} events in Silver after {time.time() - t0:.0f} s".replace(",", "."), flush=True)
            nxt += 60
        time.sleep(2)
    if done is None:
        out(f"**Quá hạn:** sau 540 giây Silver mới có {n:,}/{a.burst:,} dòng cập nhật.".replace(",", "."))
    else:
        burst = done
        out(f"Silver thấy đủ {a.burst:,} bản ghi cập nhật sau **{done:.1f} giây**, tức **{a.burst / done:,.0f} sự kiện mỗi giây** (đã gồm chu kỳ chờ của trigger).".replace(",", "."))
    # revert
    t1 = run_update("update oltp.orders set order_estimated_delivery_date = order_estimated_delivery_date - interval '1 day' where order_id in (select order_id from oltp.orders where order_id <> %s order by order_id limit %s)", (oid, a.burst))
    t1ms = int(t1 * 1000)
    deadline = time.time() + 540
    while time.time() < deadline:
        if trq(f"select count(*) from orders where src_ts_ms >= {t1ms}")[0][0] >= a.burst:
            out(f"Đã hoàn nguyên: Silver nhận đủ {a.burst:,} bản ghi hoàn nguyên sau {time.time() - t1:.1f} giây; nguồn trở về nội dung ban đầu.".replace(",", "."))
            break
        time.sleep(2)

if a.png and rows:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 3.8))
    labels = [f"lần {r['i']}" for r in rows]
    left = [0.0] * len(rows)
    for k, name, col in (("pg_kafka", "PostgreSQL → Kafka", "#8ECAE6"), ("kafka_bronze", "Kafka → Bronze", "#F4A261"), ("bronze_silver", "Bronze → Silver", "#2A9D8F")):
        vals = [r[k] for r in rows]
        ax.barh(labels, vals, left=left, label=name, color=col, edgecolor="white")
        left = [l + v for l, v in zip(left, vals)]
    for y, l in enumerate(left):
        ax.text(l + 0.4, y, f"{l:.1f} s", va="center", fontsize=11)
    ax.set_xlabel("giây từ lúc COMMIT ở nguồn", fontsize=12)
    ax.invert_yaxis()
    ax.tick_params(labelsize=11)
    ax.legend(loc="lower right", fontsize=10, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("Độ trễ đầu-cuối của luồng (trigger 30 giây)", fontsize=13, loc="left")
    fig.tight_layout()
    p = ROOT / a.png
    fig.savefig(p, dpi=200, facecolor="white")
    for sub in ("report/figures", "slides/figures"):
        if (ROOT / sub).exists():
            import shutil

            shutil.copy2(p, ROOT / sub / p.name)
    print("written", a.png)

if a.md:
    (ROOT / a.md).write_text("# P10 – Độ trễ đầu-cuối và thông lượng (Bước 9)\n\nSinh bởi `lakehouse/scripts/latency_probe.py` trong lúc luồng Spark chạy liên tục.\n\n" + "\n".join(LINES) + "\n", encoding="utf-8")
    print("written", a.md)
