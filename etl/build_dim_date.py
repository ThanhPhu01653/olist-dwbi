"""Build dw.dim_date: every day 2016-01-01 .. 2019-12-31, Brazilian holidays (package 'holidays'), Black Friday.
Idempotent (upsert on date_key). The Unknown member (-1) is created by dw.insert_unknown_members().
"""
from __future__ import annotations

import calendar
import io
from datetime import date, timedelta

import holidays
import pandas as pd
from sqlalchemy.engine import Engine

from .log import job_run

START, END = date(2016, 1, 1), date(2019, 12, 31)


def black_friday(year: int) -> date:
    thursdays = [date(year, 11, d) for d in range(1, 31) if date(year, 11, d).weekday() == 3]
    return thursdays[3] + timedelta(days=1)


def build_frame() -> pd.DataFrame:
    br = holidays.Brazil(years=range(START.year, END.year + 1))
    bf = {black_friday(y) for y in range(START.year, END.year + 1)}
    rows = []
    d = START
    while d <= END:
        iso = d.isocalendar()
        name = br.get(d)
        rows.append({
            "date_key": int(d.strftime("%Y%m%d")), "full_date": d, "day_of_month": d.day, "day_of_week": d.isoweekday(),
            "day_name": calendar.day_name[d.weekday()], "week_of_year": iso[1], "month": d.month, "month_name": calendar.month_name[d.month],
            "quarter": (d.month - 1) // 3 + 1, "year": d.year, "year_month": d.strftime("%Y-%m"),
            "year_quarter": f"{d.year}-Q{(d.month - 1) // 3 + 1}", "is_weekend": d.isoweekday() >= 6,
            "is_holiday_br": name is not None, "holiday_name": name, "is_black_friday": d in bf})
        d += timedelta(days=1)
    return pd.DataFrame(rows)


def build_dim_date(engine: Engine, batch_id: int) -> int:
    df = build_frame()
    raw = engine.raw_connection()
    try:
        with job_run(engine, batch_id, "dw.build_dim_date", "dw", "dw.dim_date") as run:
            cur = raw.cursor()
            cur.execute("CREATE TEMP TABLE tmp_dim_date (LIKE dw.dim_date INCLUDING DEFAULTS) ON COMMIT DROP")
            buf = io.StringIO()
            df.to_csv(buf, index=False, header=False, lineterminator="\n")
            buf.seek(0)
            cur.copy_expert(f"COPY tmp_dim_date ({', '.join(df.columns)}) FROM STDIN WITH (FORMAT csv)", buf)
            cols = ", ".join(c for c in df.columns if c != "date_key")
            sets = ", ".join(f"{c} = EXCLUDED.{c}" for c in df.columns if c != "date_key")
            cur.execute(f"INSERT INTO dw.dim_date (date_key, {cols}) SELECT date_key, {cols} FROM tmp_dim_date "
                        f"ON CONFLICT (date_key) DO UPDATE SET {sets}, dw_updated_at = now() "
                        f"WHERE (dw.dim_date.is_holiday_br, dw.dim_date.holiday_name) IS DISTINCT FROM (EXCLUDED.is_holiday_br, EXCLUDED.holiday_name)")
            run.rows_read = len(df)
            run.rows_inserted = cur.rowcount
            raw.commit()
    except BaseException:
        raw.rollback()
        raise
    finally:
        raw.close()
    return len(df)
