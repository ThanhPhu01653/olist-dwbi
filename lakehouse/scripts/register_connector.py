"""Register (or update) the Debezium PostgreSQL connector of the Lakehouse source and wait until it is RUNNING.

    python lakehouse/scripts/register_connector.py [--delete]
Reads lakehouse/connectors/olist-source.json, fills ${LH_PG_USER} / ${LH_PG_PASSWORD} / ${LH_PG_DB} from lakehouse/.env and PUTs the config
(idempotent: running it again just updates the config). One topic per source table: olist.<schema>.<table>.
Debezium encodes: timestamp -> microseconds since epoch (long), date -> days since epoch (int), numeric -> string (decimal.handling.mode=string).
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request

from lh_env import LH, load_env


def call(method: str, url: str, body: dict | None = None) -> tuple[int, str]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def main() -> None:
    env = load_env()
    base = f"http://127.0.0.1:{env['LH_CONNECT_PORT']}"
    spec = json.loads((LH / "connectors" / "olist-source.json").read_text(encoding="utf-8").replace("${LH_PG_USER}", env["LH_PG_USER"])
                      .replace("${LH_PG_PASSWORD}", env["LH_PG_PASSWORD"]).replace("${LH_PG_DB}", env["LH_PG_DB"]))
    name = spec["name"]
    if "--delete" in sys.argv:
        print("delete:", call("DELETE", f"{base}/connectors/{name}")[0])
        return
    code, body = call("PUT", f"{base}/connectors/{name}/config", spec["config"])
    if code not in (200, 201):
        raise SystemExit(f"registering failed: HTTP {code}: {body[:400]}")
    print(f"connector {name}: HTTP {code} (config applied)")
    t0 = time.time()
    while time.time() - t0 < 120:
        code, body = call("GET", f"{base}/connectors/{name}/status")
        st = json.loads(body) if code == 200 else {}
        c = st.get("connector", {}).get("state")
        tasks = [t.get("state") for t in st.get("tasks", [])]
        if c == "RUNNING" and tasks and all(t == "RUNNING" for t in tasks):
            print(f"state: connector RUNNING, tasks {tasks}")
            return
        if c == "FAILED" or "FAILED" in tasks:
            raise SystemExit("connector FAILED: " + json.dumps(st)[:800])
        time.sleep(3)
    raise SystemExit("timeout waiting for RUNNING: " + body[:300])


if __name__ == "__main__":
    main()
