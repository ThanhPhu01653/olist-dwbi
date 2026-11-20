"""Load the initial source data (records up to 2017-12-31) into the Lakehouse source PostgreSQL (container, port 5433).

    python lakehouse/scripts/load_source.py [--report]
Runs the project's own code (python -m etl.setup_db / etl.load_source --initial) with DB_* pointed at the container,
so the Lakehouse starts from exactly the same source state as the warehouse. The warehouse database olist_dw is not touched.
"""
from __future__ import annotations

import subprocess
import sys

from lh_env import ROOT, load_env, source_env


def run(*args: str) -> None:
    env = load_env()
    print("$ python", *args, f"   (DB {env['LH_PG_DB']} on 127.0.0.1:{env['LH_PG_PORT']})", flush=True)
    r = subprocess.run([sys.executable, *args], cwd=ROOT, env=source_env())
    if r.returncode:
        raise SystemExit(r.returncode)


if __name__ == "__main__":
    db = load_env()["LH_PG_DB"]
    if "--report" in sys.argv:
        run("-m", "etl.load_source", "--report", "--database", db)
    else:
        run("-m", "etl.setup_db", "--database", db)
        run("-m", "etl.load_source", "--initial", "--database", db)
