"""Run the data-quality tests in sql/90_tests/*.sql and store every result in etl_log.dq_check.

Each test file is ONE query returning rows (check_name, target_table, expected, actual, passed).
    python -m etl.run_tests [--only ods|dim|fact] [--batch-id N]
Prints a one-line summary and only the failing checks; exit code 1 if any check fails.
"""
from __future__ import annotations

import argparse
import sys

from sqlalchemy.engine import Engine

from . import config
from .db import get_engine
from .log import new_batch_id

TESTS_DIR = config.SQL_DIR / "90_tests"


def run_tests(engine: Engine, batch_id: int, only: str | None = None) -> tuple[int, int, list[dict]]:
    """Returns (passed, failed, failures). Files with 'eda' in the name are report-only: stored in etl_log.dq_check
    (passed = the real comparison) but never counted as failures; their summary is in run_tests.last_info."""
    passed = failed = 0
    info_total = info_match = 0
    fails: list[dict] = []
    for path in sorted(TESTS_DIR.glob("*.sql")):
        if only and only not in path.stem:
            continue
        informational = "eda" in path.stem
        sql = path.read_text(encoding="utf-8")
        raw = engine.raw_connection()      # plain psycopg2: '%' and ':' in test SQL are safe
        try:
            cur = raw.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            for check, target, expected, actual, ok in rows:
                cur.execute("INSERT INTO etl_log.dq_check (batch_id, check_name, target_table, expected, actual, passed) "
                            "VALUES (%s, %s, %s, %s, %s, %s)", (batch_id, check, target, expected, actual, bool(ok)))
                if informational:
                    info_total += 1
                    info_match += bool(ok)
                elif ok:
                    passed += 1
                else:
                    failed += 1
                    fails.append({"file": path.name, "check": check, "table": target, "expected": expected, "actual": actual})
            raw.commit()
        finally:
            raw.close()
    if not only or "orphan" in only:       # scenario test (rolled back): ODS retries rows rejected as orphans in a later batch
        from .test_orphan_retry import run_scenario
        for name, ok, detail in run_scenario(engine):
            raw = engine.raw_connection()
            try:
                raw.cursor().execute("INSERT INTO etl_log.dq_check (batch_id, check_name, target_table, expected, actual, passed) VALUES (%s, %s, 'ods.closed_deals', 'ok', %s, %s)",
                                     (batch_id, name, detail, ok))
                raw.commit()
            finally:
                raw.close()
            passed, failed = passed + ok, failed + (not ok)
            if not ok:
                fails.append({"file": "test_orphan_retry.py", "check": name, "table": "ods.closed_deals", "expected": "ok", "actual": detail})
    run_tests.last_info = (info_match, info_total)
    return passed, failed, fails


run_tests.last_info = (0, 0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", help="run only test files whose name contains this text (e.g. ods, dim, fact)")
    parser.add_argument("--batch-id", type=int)
    parser.add_argument("--database", default=config.DB_NAME)
    args = parser.parse_args()
    engine = get_engine(args.database)
    batch = args.batch_id or new_batch_id(engine)
    passed, failed, fails = run_tests(engine, batch, args.only)
    print(f"tests: {passed} passed, {failed} failed (batch {batch}); EDA cross-check (report only): {run_tests.last_info[0]}/{run_tests.last_info[1]} match")
    for f in fails:
        print(f"  FAIL [{f['file']}] {f['check']} on {f['table']}: expected {f['expected']}, actual {f['actual']}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
