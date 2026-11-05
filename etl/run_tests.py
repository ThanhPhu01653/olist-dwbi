"""Run the data-quality tests in sql/90_tests/*.sql and store every result in etl_log.dq_check.

Each test file is ONE query returning rows (check_name, target_table, expected, actual, passed).
    python -m etl.run_tests [--only ods|dim|fact] [--batch-id N]
Prints a one-line summary and only the failing checks; exit code 1 if any check fails.
"""
from __future__ import annotations

import argparse
import sys

from sqlalchemy import text
from sqlalchemy.engine import Engine

from . import config
from .db import get_engine
from .log import new_batch_id

TESTS_DIR = config.SQL_DIR / "90_tests"


def run_tests(engine: Engine, batch_id: int, only: str | None = None) -> tuple[int, int, list[dict]]:
    passed = failed = 0
    fails: list[dict] = []
    for path in sorted(TESTS_DIR.glob("*.sql")):
        if only and only not in path.stem:
            continue
        sql = path.read_text(encoding="utf-8")
        with engine.begin() as conn:
            rows = conn.exec_driver_sql(sql).fetchall()
            for check, target, expected, actual, ok in rows:
                conn.execute(text(
                    "INSERT INTO etl_log.dq_check (batch_id, check_name, target_table, expected, actual, passed) "
                    "VALUES (:b, :c, :t, :e, :a, :p)"), {"b": batch_id, "c": check, "t": target, "e": expected, "a": actual, "p": bool(ok)})
                if ok:
                    passed += 1
                else:
                    failed += 1
                    fails.append({"file": path.name, "check": check, "table": target, "expected": expected, "actual": actual})
    return passed, failed, fails


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", help="run only test files whose name contains this text (e.g. ods, dim, fact)")
    parser.add_argument("--batch-id", type=int)
    parser.add_argument("--database", default=config.DB_NAME)
    args = parser.parse_args()
    engine = get_engine(args.database)
    batch = args.batch_id or new_batch_id(engine)
    passed, failed, fails = run_tests(engine, batch, args.only)
    print(f"tests: {passed} passed, {failed} failed (batch {batch})")
    for f in fails:
        print(f"  FAIL [{f['file']}] {f['check']} on {f['table']}: expected {f['expected']}, actual {f['actual']}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
