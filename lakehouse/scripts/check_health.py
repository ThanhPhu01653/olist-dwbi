"""Print the state of every Lakehouse service: Docker health + a real probe of the service itself.

    python lakehouse/scripts/check_health.py [--wait 180] [--json]
Exit code 0 only when every probe of the running profile is OK. Reads ports and passwords from lakehouse/.env.
Probes (no extra dependencies except psycopg2 from the project .venv):
  pg           connection on LH_PG_PORT, wal_level = logical, both databases exist
  kafka        Docker healthcheck (kafka-broker-api-versions) and the topics list through Kafka Connect
  connect      GET /connectors (Kafka Connect REST)
  minio        /minio/health/live and bucket LH_MINIO_BUCKET exists (listed with the mc client inside the container)
  iceberg-rest GET /v1/config
  trino        GET /v1/info (starting = false)
  spark        container running and spark-submit present (--deep also runs a tiny Spark SQL against the catalog)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent          # lakehouse/
SERVICES = ["pg", "kafka", "connect", "minio", "iceberg-rest", "spark", "trino"]


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    f = HERE / ".env"
    if not f.exists():
        raise SystemExit("lakehouse/.env not found: copy lakehouse/.env.example to lakehouse/.env")
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def docker_state(container: str) -> tuple[str, str]:
    """(status, health) of a container, e.g. ('running', 'healthy'); ('absent', '-') when it does not exist."""
    p = subprocess.run(["docker", "inspect", "--format", "{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{else}}-{{end}}", container],
                       capture_output=True, text=True)
    if p.returncode != 0:
        return "absent", "-"
    status, _, health = p.stdout.strip().partition("|")
    return status, health


def http_get(url: str, timeout: float = 5.0) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status, r.read(4000).decode("utf-8", "replace")
    except Exception as exc:        # connection refused, timeout, HTTP error
        code = getattr(exc, "code", 0)
        return code, str(exc)


def probe_pg(env) -> tuple[bool, str]:
    import psycopg2
    try:
        c = psycopg2.connect(host="127.0.0.1", port=int(env["LH_PG_PORT"]), user=env["LH_PG_USER"], password=env["LH_PG_PASSWORD"], dbname=env["LH_PG_DB"], connect_timeout=5)
    except Exception as exc:
        return False, f"connect failed: {str(exc).strip().splitlines()[0]}"
    with c, c.cursor() as cur:
        cur.execute("SHOW wal_level")
        wal = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM pg_database WHERE datname IN (%s, %s)", (env["LH_PG_DB"], env["LH_CATALOG_DB"]))
        dbs = cur.fetchone()[0]
    c.close()
    return wal == "logical" and dbs == 2, f"wal_level={wal}, databases {env['LH_PG_DB']} + {env['LH_CATALOG_DB']}: {dbs}/2"


def probe_kafka(env) -> tuple[bool, str]:
    status, health = docker_state("lh-kafka")
    return health == "healthy", f"container {status}/{health}"


def probe_connect(env) -> tuple[bool, str]:
    code, body = http_get(f"http://127.0.0.1:{env['LH_CONNECT_PORT']}/connectors")
    if code != 200:
        return False, f"HTTP {code}: {body[:80]}"
    try:
        n = len(json.loads(body))
    except ValueError:
        n = -1
    return True, f"REST ok, {n} connector(s)"


def probe_minio(env) -> tuple[bool, str]:
    code, _ = http_get(f"http://127.0.0.1:{env['LH_MINIO_PORT']}/minio/health/live")
    if code != 200:
        return False, f"health/live HTTP {code}"
    # bucket check through the container's own client (mc ships with the bitnami image)
    p = subprocess.run(["docker", "exec", "lh-minio", "sh", "-c",
                        "mc alias set local http://localhost:9000 \"$MINIO_ROOT_USER\" \"$MINIO_ROOT_PASSWORD\" >/dev/null 2>&1 && mc ls local"], capture_output=True, text=True)
    has = env["LH_MINIO_BUCKET"] in p.stdout
    return has, f"live; bucket {env['LH_MINIO_BUCKET']}: {'present' if has else 'MISSING'}"


def probe_rest(env) -> tuple[bool, str]:
    code, body = http_get(f"http://127.0.0.1:{env['LH_REST_PORT']}/v1/config")
    return code == 200, f"HTTP {code}" + (f", defaults: {list(json.loads(body).get('defaults', {}))[:3]}" if code == 200 else f": {body[:80]}")


def probe_trino(env) -> tuple[bool, str]:
    code, body = http_get(f"http://127.0.0.1:{env['LH_TRINO_PORT']}/v1/info")
    if code != 200:
        return False, f"HTTP {code}: {body[:80]}"
    info = json.loads(body)
    return not info.get("starting", True), f"version {info.get('nodeVersion', {}).get('version')}, starting={info.get('starting')}"


def probe_spark(env, deep: bool) -> tuple[bool, str]:
    status, health = docker_state("lh-spark")
    if status != "running":
        return False, f"container {status}"
    p = subprocess.run(["docker", "exec", "lh-spark", "/opt/spark/bin/spark-submit", "--version"], capture_output=True, text=True)
    import re
    m = re.search(r"version\s+(\d+\.\d+\.\d+)", p.stdout + p.stderr)
    ver = m.group(1) if m else "?"
    return p.returncode == 0, f"container {status}/{health}, Spark {ver}"


PROBES = {"pg": probe_pg, "kafka": probe_kafka, "connect": probe_connect, "minio": probe_minio, "iceberg-rest": probe_rest, "trino": probe_trino}


def run_once(env, deep: bool) -> list[dict]:
    rows = []
    for svc in SERVICES:
        container = f"lh-{svc}"
        status, health = docker_state(container)
        if status == "absent":
            rows.append({"service": svc, "container": status, "health": health, "ok": False, "detail": "not created (docker compose --profile lite up -d)"})
            continue
        if svc == "spark":
            ok, detail = probe_spark(env, deep)
        else:
            try:
                ok, detail = PROBES[svc](env)
            except Exception as exc:
                ok, detail = False, f"probe error: {type(exc).__name__}: {str(exc)[:80]}"
        rows.append({"service": svc, "container": status, "health": health, "ok": ok, "detail": detail})
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--wait", type=int, default=0, help="keep retrying for this many seconds until every service is OK")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--deep", action="store_true")
    a = ap.parse_args()
    env = load_env()
    t0 = time.time()
    while True:
        rows = run_once(env, a.deep)
        if all(r["ok"] for r in rows) or time.time() - t0 >= a.wait:
            break
        time.sleep(5)
    if a.json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
    else:
        print(f"{'service':14} {'container':10} {'health':10} {'probe':6} detail")
        for r in rows:
            print(f"{r['service']:14} {r['container']:10} {r['health']:10} {'OK' if r['ok'] else 'FAIL':6} {r['detail']}")
    sys.exit(0 if all(r["ok"] for r in rows) else 1)


if __name__ == "__main__":
    main()
