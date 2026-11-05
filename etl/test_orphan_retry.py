"""Scenario test for the orphan retry of the ODS layer:  python -m etl.test_orphan_retry

A child row rejected as 'orphan' (parent missing) must be loaded in a LATER batch once its parent is there, and must then disappear
from etl_log.rejected_rows. Example from the data: the deal of MQL b91cf881... (won 2018-03-06, first contact 2018-03-08).
Everything runs inside ONE transaction on the real database and is rolled back at the end, so no data changes.
  step 1  the MQL is missing in ODS and staging, the deal is staged -> ods.load_closed_deals rejects it as orphan
  step 2  the MQL arrives in a later batch -> ods.load_mql + ods.load_closed_deals: the deal is loaded, the rejection record is gone
  step 3  a further batch does not duplicate anything
"""
from __future__ import annotations

import sys

from . import config
from .db import get_engine
from .log import new_batch_id

PREFERRED = "b91cf8812365f50ff4bda4bcd6206b05"


def run_scenario(engine) -> list[tuple[str, bool, str]]:
    b1, b2, b3 = new_batch_id(engine), new_batch_id(engine), new_batch_id(engine)
    out: list[tuple[str, bool, str]] = []
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        cur.execute("SELECT mql_id FROM ods.closed_deals ORDER BY (mql_id = %s) DESC, mql_id LIMIT 1", (PREFERRED,))
        row = cur.fetchone()
        if row is None:
            return [("orphan retry: scenario needs at least one deal in ODS (skipped)", True, "no deals loaded")]
        mql = row[0]
        cur.execute("DELETE FROM ods.closed_deals WHERE mql_id = %s", (mql,))
        cur.execute("DELETE FROM ods.mql WHERE mql_id = %s", (mql,))
        cur.execute("CREATE TEMP TABLE hold_mql ON COMMIT DROP AS SELECT * FROM staging.stg_mql WHERE mql_id = %s", (mql,))
        cur.execute("DELETE FROM staging.stg_mql WHERE mql_id = %s", (mql,))
        cur.execute("UPDATE staging.stg_closed_deals SET load_batch_id = %s WHERE mql_id = %s", (b1, mql))
        cur.execute("DELETE FROM etl_log.rejected_rows WHERE job_name = 'ods.load_closed_deals' AND record ->> 'mql_id' = %s", (mql,))

        def count(sql, *p):
            cur.execute(sql, p)
            return cur.fetchone()[0]

        cur.execute("CALL ods.load_closed_deals(%s, 0, 0, 0)", (b1,))
        in_ods = count("SELECT count(*) FROM ods.closed_deals WHERE mql_id = %s", mql)
        rej = count("SELECT count(*) FROM etl_log.rejected_rows WHERE job_name = 'ods.load_closed_deals' AND reason LIKE 'orphan:%%' AND record ->> 'mql_id' = %s", mql)
        out.append(("orphan retry 1: deal whose MQL has not arrived is rejected as orphan, not loaded", in_ods == 0 and rej == 1, f"in ods {in_ods}, orphan rejections {rej}"))

        cur.execute("INSERT INTO staging.stg_mql SELECT * FROM hold_mql")
        cur.execute("UPDATE staging.stg_mql SET load_batch_id = %s WHERE mql_id = %s", (b2, mql))
        cur.execute("CALL ods.load_mql(%s, 0, 0, 0)", (b2,))
        cur.execute("CALL ods.load_closed_deals(%s, 0, 0, 0)", (b2,))      # nothing staged in batch b2: only the retry can load the deal
        in_ods = count("SELECT count(*) FROM ods.closed_deals WHERE mql_id = %s", mql)
        rej = count("SELECT count(*) FROM etl_log.rejected_rows WHERE job_name = 'ods.load_closed_deals' AND record ->> 'mql_id' = %s", mql)
        out.append(("orphan retry 2: once the MQL is in ODS the deal is loaded in a later batch and its rejection record is removed", in_ods == 1 and rej == 0, f"in ods {in_ods}, rejections {rej}"))

        cur.execute("CALL ods.load_closed_deals(%s, 0, 0, 0)", (b3,))
        in_ods = count("SELECT count(*) FROM ods.closed_deals WHERE mql_id = %s", mql)
        out.append(("orphan retry 3: a further batch does not duplicate the deal", in_ods == 1, f"in ods {in_ods}"))
    finally:
        raw.rollback()
        raw.close()
    return out


def main() -> None:
    results = run_scenario(get_engine(config.DB_NAME))
    for name, ok, detail in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name}  ({detail})")
    sys.exit(0 if all(r[1] for r in results) else 1)


if __name__ == "__main__":
    main()
