"""Iceberg time travel on the Lakehouse (Step 7): snapshots, reading old versions, rollback, status history, schema evolution, table statistics.

    python lakehouse/scripts/time_travel.py [--md handoff/2026-11-19-P10-timetravel.md]

Reads of old versions use the real table silver.orders (read only). Everything that changes data (the "mistake" and its rollback, the schema change) is done on a copy,
iceberg.ops.orders_tt, so Silver is never touched.
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import timezone
from pathlib import Path

from trino.dbapi import connect

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lh_env import ROOT, load_env  # noqa: E402

env = load_env()
conn = connect(host="127.0.0.1", port=int(env["LH_TRINO_PORT"]), user="time_travel", catalog="iceberg", schema="silver")
LINES: list[str] = []


def q(sql, fetch=True):
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall() if fetch else cur.fetchall()
    return [c[0] for c in cur.description] if cur.description else [], rows


def out(text=""):
    print(text)
    LINES.append(text)


def table(cols, rows):
    out("| " + " | ".join(cols) + " |")
    out("| " + " | ".join("---" for _ in cols) + " |")
    for r in rows:
        out("| " + " | ".join("" if v is None else (fmt(v) if isinstance(v, int) and not isinstance(v, bool) and abs(v) < 10**12 else str(v)) for v in r) + " |")
    out()


def fmt(n):
    return f"{n:,}".replace(",", ".") if isinstance(n, int) else str(n)


def scalar(sql):
    return q(sql)[1][0][0]


ap = argparse.ArgumentParser()
ap.add_argument("--md")
a = ap.parse_args()

out("## 1. Lịch sử snapshot của bảng thật `silver.orders` (chỉ đọc)")
cols, rows = q('select snapshot_id, committed_at, operation, summary[\'total-records\'] from iceberg.silver."orders$snapshots" order by committed_at')
out(f"Bảng có {len(rows)} snapshot (mỗi micro-batch của luồng Spark tạo một hoặc hai snapshot khi MERGE). Ba snapshot đại diện:")
pick = [rows[0], rows[len(rows) // 2], rows[-1]]
table(["snapshot_id", "committed_at (UTC)", "operation", "tổng số dòng ghi trong snapshot"], [[str(r[0]), r[1].astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'), r[2], int(r[3])] for r in pick])
res = []
for r in pick:
    t0 = time.perf_counter()
    n = scalar(f"select count(*) from iceberg.silver.orders for version as of {r[0]}")
    res.append([str(r[0]), r[1].astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'), n, round(time.perf_counter() - t0, 2)])
out("Đọc lại từng phiên bản cũ bằng `FOR VERSION AS OF` (số đơn tại thời điểm đó, không đụng dữ liệu hiện tại):")
table(["snapshot_id", "committed_at (UTC)", "số đơn đọc được", "giây"], res)
mid_ts = pick[1][1].astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
n_ts = scalar(f"select count(*) from iceberg.silver.orders for timestamp as of timestamp '{mid_ts} UTC'")
out(f"Cũng đọc được theo thời gian: `FOR TIMESTAMP AS OF TIMESTAMP '{mid_ts} UTC'` trả về {fmt(n_ts)} đơn"+ f" (hiện tại {fmt(scalar('select count(*) from iceberg.silver.orders'))} đơn).")
out()

out("## 2. Sửa nhầm rồi rollback (trên bản sao `ops.orders_tt`)")
q("drop table if exists iceberg.ops.orders_tt")
q("create table iceberg.ops.orders_tt as select * from iceberg.silver.orders")
snaps = q('select snapshot_id from iceberg.ops."orders_tt$snapshots" order by committed_at')[1]
s1 = snaps[0][0]
n0 = scalar("select count(*) from iceberg.ops.orders_tt")
canc0 = scalar("select count(*) from iceberg.ops.orders_tt where order_status = 'canceled'")
out(f"Bản sao: {fmt(n0)} đơn, {fmt(canc0)} đơn ở trạng thái `canceled`; snapshot ban đầu `{s1}`.")
q("update iceberg.ops.orders_tt set order_status = 'canceled' where order_status = 'delivered'")
canc1 = scalar("select count(*) from iceberg.ops.orders_tt where order_status = 'canceled'")
s2 = q('select snapshot_id from iceberg.ops."orders_tt$snapshots" order by committed_at desc limit 1')[1][0][0]
out(f"Thao tác nhầm: `UPDATE ... SET order_status = 'canceled' WHERE order_status = 'delivered'` → {fmt(canc1)} đơn `canceled` (snapshot mới `{s2}`).")
old = scalar(f"select count(*) from iceberg.ops.orders_tt for version as of {s1} where order_status = 'canceled'")
out(f"Phiên bản cũ vẫn còn nguyên: đọc `FOR VERSION AS OF {s1}` thấy {fmt(old)} đơn `canceled`.")
t0 = time.perf_counter()
q(f"call iceberg.system.rollback_to_snapshot('ops', 'orders_tt', {s1})")
sec = time.perf_counter() - t0
canc2 = scalar("select count(*) from iceberg.ops.orders_tt where order_status = 'canceled'")
out(f"`CALL iceberg.system.rollback_to_snapshot('ops', 'orders_tt', {s1})` mất {sec:.2f} giây (chỉ đổi con trỏ metadata, không chép dữ liệu); sau đó `canceled` = {fmt(canc2)}, đúng bằng trước khi sửa: **{'đúng' if canc2 == canc0 else 'SAI'}**.")
same = scalar("select count(*) from (select * from iceberg.ops.orders_tt except select * from iceberg.silver.orders) x")
out(f"So với bảng gốc `silver.orders` sau rollback: số dòng khác nhau = {same}.")
out()

out("## 3. \"Đơn này ở trạng thái nào lúc T?\" (`silver.order_status_history`, dạng SCD2)")
cols, rows = q("""select order_id from iceberg.silver.order_status_history group by order_id having count(*) = 4 order by order_id limit 1""")
oid = rows[0][0]
cols, rows = q(f"select status, cast(valid_from as varchar), cast(valid_to as varchar), is_current from iceberg.silver.order_status_history where order_id = '{oid}' order by valid_from")
out(f"Đơn `{oid}` có {len(rows)} phiên bản trạng thái:")
table(["status", "valid_from", "valid_to", "is_current"], rows)
mid = rows[len(rows) // 2][1][:19]
st = q(f"select status from iceberg.silver.order_status_history where order_id = '{oid}' and valid_from <= timestamp '{mid} UTC' and (valid_to is null or valid_to > timestamp '{mid} UTC')")[1]
out(f"Truy vấn `valid_from <= T < valid_to` với T = {mid} UTC trả về trạng thái `{st[0][0]}`.")
out()

out("## 4. Tiến hoá lược đồ (trên bản sao)")
q("alter table iceberg.ops.orders_tt add column note varchar")
cols, rows = q("select count(note), count(*) from iceberg.ops.orders_tt")
out(f"`ALTER TABLE ... ADD COLUMN note varchar` không ghi lại dữ liệu cũ: cột mới có {rows[0][0]} giá trị khác NULL trên {fmt(rows[0][1])} dòng (đọc bình thường, file Parquet cũ giữ nguyên).")
q("alter table iceberg.ops.orders_tt drop column note")
out("`DROP COLUMN note` cũng chỉ đổi metadata. Iceberg theo dõi cột bằng ID chứ không bằng tên hay vị trí, nên thêm/bớt cột không làm hỏng các snapshot cũ.")
out()

out("## 5. Thống kê bảng")
cols, rows = q('select count(*), sum(file_size_in_bytes), sum(record_count) from iceberg.silver."orders$files"')
out(f"`silver.orders`: {rows[0][0]} file dữ liệu, {rows[0][1] / 1048576:.1f} MiB, {fmt(rows[0][2])} dòng (file của snapshot hiện tại; các snapshot cũ còn giữ thêm file riêng cho tới khi dọn bằng expire_snapshots).")
cols, rows = q("show stats for iceberg.silver.orders")
table(cols[:6], [[r[i] for i in range(6)] for r in rows[:6]])
q("drop table iceberg.ops.orders_tt")
out("Đã xoá bản sao `ops.orders_tt`; `silver.orders` không bị thay đổi trong suốt phần này.")

if a.md:
    p = ROOT / a.md
    p.write_text("# P10 – Time travel Iceberg (Bước 7)\n\nSinh bởi `lakehouse/scripts/time_travel.py`; số lấy từ lần chạy thật.\n\n" + "\n".join(LINES) + "\n", encoding="utf-8")
    print("written", a.md)
