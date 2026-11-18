"""CLI:  python -m api_ingest.run --source all|ibge|bcb|holidays|weather [--offline] [--fetch-only] [--database olist_dw]

Steps: collect (API -> landing zone) -> stage (landing zone -> api.stg_api_*) -> ODS (clean, FX, IPCA, holidays, city match).
--offline   skip the API calls and load what is already in data/raw/api/ (used by rebuild_all.py: a rebuild never needs the network)
--fetch-only  only collect into the landing zone
A failing API is logged (etl_log.api_call, etl_log.job_run) and never stops the others or the main pipeline.
"""
from __future__ import annotations

import argparse
import sys
import time

from sqlalchemy.engine import Engine

from etl import config as etl_config
from etl.db import get_engine
from etl.log import job_run, new_batch_id

from . import config
from .collect import Collector
from .stage import stage_all


def run_api(engine: Engine, batch_id: int, sources: list[str], fetch: bool = True, stage: bool = True, ods: bool = True) -> dict:
    """Collect (optional), stage and clean the API data inside the given batch. Returns a summary dict."""
    summary: dict = {"fetch": {}, "stage": {}, "ods": {}}
    if fetch:
        col = Collector(engine, batch_id)
        t0 = time.perf_counter()
        with job_run(engine, batch_id, "api.collect", "api") as run:
            outcome = col.collect(sources)
            run.rows_read = sum(c["records"] or 0 for c in col.calls)
            run.rows_inserted = sum(1 for c in col.calls if not c["error"])
            run.rows_rejected = sum(1 for c in col.calls if c["error"])
            failed = {s: e for s, e in outcome.items() if e}
            run.message = "; ".join(f"{s}: {e}" for s, e in failed.items()) or None   # logged, never raised: the pipeline goes on
        summary["fetch"] = {"calls": len(col.calls), "failed": failed, "seconds": round(time.perf_counter() - t0, 1)}
    if stage:
        summary["stage"] = stage_all(engine, batch_id)
    if stage and ods:
        from .ods import run_ods
        summary["ods"] = run_ods(engine, batch_id)
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default="all", choices=["all", *config.SOURCES])
    ap.add_argument("--database", default=etl_config.DB_NAME)
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--fetch-only", action="store_true")
    a = ap.parse_args()
    sources = config.SOURCES if a.source == "all" else [a.source]
    engine = get_engine(a.database)
    batch = new_batch_id(engine)
    s = run_api(engine, batch, sources, fetch=not a.offline, stage=not a.fetch_only, ods=not a.fetch_only)
    print(f"api batch {batch}: {s}")
    sys.exit(1 if s["fetch"].get("failed") else 0)


if __name__ == "__main__":
    main()
