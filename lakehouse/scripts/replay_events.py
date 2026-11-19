"""Replay the data after 2017-12-31 into the Lakehouse source PostgreSQL as a live stream of changes (Debezium turns them into Kafka events).

    python lakehouse/scripts/replay_events.py [--speed S] [--batch-events N] [--until YYYY-MM-DD] [--limit-events N] [--dry-run]

What happens, in simulated time order (the CSV timestamps are the clock):
  - a new order is INSERTed at its purchase time with status 'created' (with its customer, items and payments);
  - then UPDATEd at each milestone it really reached: approved (order_approved_at), shipped (order_delivered_carrier_date),
    delivered (order_delivered_customer_date); orders that ended as canceled / unavailable / invoiced / processing get that final status
    at the last time known for them. The last UPDATE sets every timestamp of the CSV, so the final row equals the CSV row;
  - reviews are INSERTed at review_creation_date, MQLs at first_contact_date (earlier of that and the deal date), closed deals at won_date.
So Bronze receives the real life cycle of every order, not only its final state (the warehouse of chapter 3 only ever sees the final one).

--speed S      simulated seconds per real second (0 = no pacing, as fast as possible; 86400 = one simulated day per real second)
--batch-events events per source transaction (default 200); inserts of a batch are grouped per table, updates keep their order
--until        stop after this simulated date (inclusive); the next run continues where this one stopped
Progress is stored in the source database (public.replay_state, same transaction as the events), so a re-run never applies an event twice
and never moves an order back to an earlier status. Only schemas oltp and crm are captured by Debezium; public is not.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

from lh_env import LH, ROOT, load_env

ECOM = ROOT / "data" / "raw" / "ecommerce"
MKT = ROOT / "data" / "raw" / "marketing"
CUTOFF = pd.Timestamp("2018-01-01")            # first instant that is not in the initial load

INSERT_ORDER = ["oltp.customers", "oltp.orders", "oltp.order_items", "oltp.order_payments", "oltp.order_reviews", "crm.mql", "crm.closed_deals"]
TS_COLS = {"approved": "order_approved_at", "shipped": "order_delivered_carrier_date", "delivered": "order_delivered_customer_date"}


def rd(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")


def none(v):
    return None if v == "" or v is pd.NaT else v


def build_events(cur) -> tuple[list, dict]:
    """All events after the initial load, sorted by (simulated time, sequence). Event = (time, seq, op, table, payload)."""
    have = {}
    for t, col in [("oltp.orders", "order_id"), ("crm.mql", "mql_id"), ("crm.closed_deals", "mql_id")]:
        cur.execute(f"SELECT {col} FROM {t}")
        have[t] = {r[0] for r in cur.fetchall()}
    ev: list = []
    seq = 0

    def add(t, op, table, payload):
        nonlocal seq
        seq += 1
        ev.append((t, seq, op, table, payload))

    orders = rd(ECOM / "olist_orders_dataset.csv")
    ptime = pd.to_datetime(orders["order_purchase_timestamp"], errors="coerce")
    orders = orders[(ptime >= CUTOFF) & ~orders["order_id"].isin(have["oltp.orders"]) & ptime.notna()].copy()
    orders["_p"] = pd.to_datetime(orders["order_purchase_timestamp"])
    for k, c in TS_COLS.items():                    # parse once (vectorised); per-row parsing was 100 s
        orders["_" + k] = pd.to_datetime(orders[c], errors="coerce")
    ids = set(orders["order_id"])
    cust = rd(ECOM / "olist_customers_dataset.csv").set_index("customer_id")
    items = rd(ECOM / "olist_order_items_dataset.csv"); items = items[items["order_id"].isin(ids)]
    pays = rd(ECOM / "olist_order_payments_dataset.csv"); pays = pays[pays["order_id"].isin(ids)]
    revs = rd(ECOM / "olist_order_reviews_dataset.csv"); revs = revs[revs["order_id"].isin(ids)]
    items_by, pays_by = defaultdict(list), defaultdict(list)          # dict lookups: groupby().get_group() per order took 30 s
    for d in items.to_dict("records"):
        items_by[d["order_id"]].append(d)
    for d in pays.to_dict("records"):
        pays_by[d["order_id"]].append(d)
    purchase = dict(zip(orders["order_id"], orders["_p"]))

    # order life cycle
    for r in orders.to_dict("records"):
        p = r["_p"]
        add(p, "i", "oltp.customers", dict(customer_id=r["customer_id"], **{k: cust.at[r["customer_id"], k] for k in cust.columns}))
        base = {k: r[k] for k in ["order_id", "customer_id", "order_purchase_timestamp", "order_estimated_delivery_date"]}
        base.update(order_status="created", order_approved_at="", order_delivered_carrier_date="", order_delivered_customer_date="")
        add(p, "i", "oltp.orders", base)
        for d in items_by.get(r["order_id"], ()):
            add(p, "i", "oltp.order_items", d)
        for d in pays_by.get(r["order_id"], ()):
            add(p, "i", "oltp.order_payments", d)
        ts = {k: r["_" + k] for k in TS_COLS}
        final = r["order_status"]
        ms = []                                   # (status, time)
        if final != "created":
            if pd.notna(ts["approved"]) and final in ("approved", "invoiced", "processing", "shipped", "delivered", "canceled", "unavailable"):
                ms.append(("approved", ts["approved"]))
            if pd.notna(ts["shipped"]) and final in ("shipped", "delivered", "canceled", "unavailable"):
                ms.append(("shipped", ts["shipped"]))
            if pd.notna(ts["delivered"]) and final == "delivered":
                ms.append(("delivered", ts["delivered"]))
            if not ms or ms[-1][0] != final:       # final status without its own timestamp (canceled, invoiced, ...): at the last known time
                last = max([p] + [t for _, t in ms] + [t for t in ts.values() if pd.notna(t)])
                ms.append((final, last))
        t_prev = p
        for i, (st, t) in enumerate(ms):
            t = max(t, t_prev)
            t_prev = t
            upd = {"order_status": st}
            if i == len(ms) - 1:                   # the last update completes the row exactly as in the CSV
                upd.update({c: r[c] for c in TS_COLS.values() if r[c] != ""})
            elif st in TS_COLS:
                upd[TS_COLS[st]] = r[TS_COLS[st]]
            add(t, "u", "oltp.orders", {"order_id": r["order_id"], "set": upd})

    for d in revs.to_dict("records"):
        rt = pd.to_datetime(d["review_creation_date"], errors="coerce")
        p = purchase[d["order_id"]]
        add(p if pd.isna(rt) else max(rt, p), "i", "oltp.order_reviews", d)

    # marketing funnel
    mql = rd(MKT / "olist_marketing_qualified_leads_dataset.csv")
    deals = rd(MKT / "olist_closed_deals_dataset.csv")
    new_deals = deals[~deals["mql_id"].isin(have["crm.closed_deals"])].copy()
    new_deals = new_deals[pd.to_datetime(new_deals["won_date"], errors="coerce") >= CUTOFF]
    won = dict(zip(new_deals["mql_id"], pd.to_datetime(new_deals["won_date"])))
    new_mql = mql[~mql["mql_id"].isin(have["crm.mql"])]
    for d in new_mql.to_dict("records"):
        t = pd.to_datetime(d["first_contact_date"], errors="coerce")
        if d["mql_id"] in won:
            t = min(t, won[d["mql_id"]] - pd.Timedelta(seconds=1)) if pd.notna(t) else won[d["mql_id"]] - pd.Timedelta(seconds=1)
        add(t, "i", "crm.mql", d)
    for d in new_deals.to_dict("records"):
        add(pd.to_datetime(d["won_date"]), "i", "crm.closed_deals", d)

    ev.sort(key=lambda e: (e[0], e[1]))
    stats = {"orders": len(orders), "events": len(ev)}
    return ev, stats


def table_columns(cur, table: str) -> list[str]:
    schema, name = table.split(".")
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema=%s AND table_name=%s AND is_generated='NEVER' "
                "AND coalesce(identity_generation,'')<>'ALWAYS' ORDER BY ordinal_position", (schema, name))
    return [r[0] for r in cur.fetchall()]


def apply_batch(cur, batch: list, cols: dict) -> None:
    """Inserts grouped per table (parents first), then the updates in their order."""
    by_table: dict[str, list] = {}
    for _t, _s, op, table, payload in batch:
        if op == "i":
            by_table.setdefault(table, []).append(payload)
    for table in INSERT_ORDER:
        rows = by_table.get(table)
        if not rows:
            continue
        c = cols[table]
        execute_values(cur, f"INSERT INTO {table} ({', '.join(c)}) VALUES %s ON CONFLICT DO NOTHING",
                       [tuple(none(r.get(k, "")) for k in c) for r in rows], page_size=500)
    for _t, _s, op, table, payload in batch:
        if op == "u":
            sets = payload["set"]
            cur.execute(f"UPDATE {table} SET " + ", ".join(f"{k} = %s" for k in sets) + " WHERE order_id = %s", [none(v) for v in sets.values()] + [payload["order_id"]])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--speed", type=float, default=0.0)
    ap.add_argument("--batch-events", type=int, default=200)
    ap.add_argument("--until")
    ap.add_argument("--limit-events", type=int)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    env = load_env()
    conn = psycopg2.connect(host="127.0.0.1", port=int(env["LH_PG_PORT"]), user=env["LH_PG_USER"], password=env["LH_PG_PASSWORD"], dbname=env["LH_PG_DB"])
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS public.replay_state (k text PRIMARY KEY, v text NOT NULL, updated_at timestamptz NOT NULL DEFAULT now())")
    conn.commit()
    cur.execute("SELECT v FROM public.replay_state WHERE k = 'last_seq'")
    row = cur.fetchone()
    last_seq = int(row[0]) if row else 0

    t0 = time.perf_counter()
    events, stats = build_events(cur)
    conn.rollback()
    print(f"built {stats['events']:,} events for {stats['orders']:,} new orders in {time.perf_counter() - t0:.1f}s; "
          f"simulated period {events[0][0]:%Y-%m-%d} .. {events[-1][0]:%Y-%m-%d}; already applied up to seq {last_seq}", flush=True)
    c = Counter((e[3], e[2]) for e in events)
    for (t, op), n in sorted(c.items()):
        print(f"  {t:24} {'INSERT' if op == 'i' else 'UPDATE':6} {n:>9,}")
    if a.dry_run:
        return
    pending = [e for e in events if e[1] > last_seq]
    if a.until:
        pending = [e for e in pending if e[0] < pd.Timestamp(a.until) + pd.Timedelta(days=1)]
    if a.limit_events:
        pending = pending[: a.limit_events]
    cols = {t: table_columns(cur, t) for t in INSERT_ORDER}
    conn.rollback()
    done = 0
    start = time.perf_counter()
    t_sim_prev = pending[0][0] if pending else None
    for i in range(0, len(pending), a.batch_events):
        batch = pending[i: i + a.batch_events]
        apply_batch(cur, batch, cols)
        cur.execute("INSERT INTO public.replay_state (k, v) VALUES ('last_seq', %s) ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v, updated_at = now()", (str(batch[-1][1]),))
        conn.commit()
        done += len(batch)
        if a.speed > 0:
            gap = (batch[-1][0] - t_sim_prev).total_seconds() / a.speed
            t_sim_prev = batch[-1][0]
            if gap > 0:
                time.sleep(min(gap, 30))
        if (i // a.batch_events) % 50 == 0:
            el = time.perf_counter() - start
            print(f"  {done:>9,}/{len(pending):,} events  sim time {batch[-1][0]:%Y-%m-%d %H:%M}  {done / max(el, 1e-9):,.0f} events/s", flush=True)
    el = time.perf_counter() - start
    summary = {"events_applied": done, "seconds": round(el, 1), "events_per_second": round(done / el, 1) if el else None, "speed": a.speed,
               "batch_events": a.batch_events, "finished_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    print("replay finished:", json.dumps(summary))
    cur.execute("INSERT INTO public.replay_state (k, v) VALUES ('last_summary', %s) ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v, updated_at = now()", (json.dumps(summary),))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    sys.exit(main())
