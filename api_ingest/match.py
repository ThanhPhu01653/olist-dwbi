"""Match Olist (state, city) pairs to IBGE municipalities in four tiers and count the match rate after every tier.

 1. exact       lower(IBGE name) = Olist city, same state                                   (SQL: ods.match_city_exact)
 2. normalized  equal after unaccent + lower case + removing apostrophes / hyphens / spaces (SQL: ods.match_city_exact)
 3. fuzzy       rapidfuzz ratio >= FUZZY_THRESHOLD and the runner-up at least FUZZY_GAP points lower, same state only
 4. override    seeds/city_ibge_override.csv (hand-checked spelling variants)
Pairs that no tier matches go to etl_log.rejected_rows with the reason; nothing is dropped silently. Everything is recomputed on each run
from the current ODS, so it is idempotent and independent of the order of batches.
"""
from __future__ import annotations

import csv

import pandas as pd
from rapidfuzz import fuzz, process
from sqlalchemy import text
from sqlalchemy.engine import Engine

from etl.log import job_run
from etl.procs import call_procedures

from . import config

FUZZY_THRESHOLD = 95      # chosen by reading the candidates: every pair >= 95 was a true spelling variant; 90-94 already contains wrong ones
FUZZY_GAP = 10            # the second best candidate must be at least 10 points lower ("only one candidate")
OVERRIDE_CSV = config.ROOT / "seeds" / "city_ibge_override.csv"


def fuzzy_pick(city: str, candidates: list[tuple[str, int]], threshold: int = FUZZY_THRESHOLD, gap: int = FUZZY_GAP):
    """candidates: [(name_key, ibge_code)] of one state. Returns (ibge_code, score) when exactly one candidate qualifies, else None."""
    if not candidates:
        return None
    found = process.extract(city, [k for k, _ in candidates], scorer=fuzz.ratio, limit=2)
    best = found[0]
    second = found[1][1] if len(found) > 1 else 0
    if best[1] >= threshold and best[1] - second >= gap:
        return candidates[best[2]][1], round(best[1], 1)
    return None


def match_cities(engine: Engine, batch_id: int) -> dict[str, dict]:
    """Run the four tiers; returns {method: {pairs, zips}} including 'unmatched'."""
    call_procedures(engine, batch_id, "api_ods", [("ods.match_city_exact", "ods.city_ibge_match")])
    with job_run(engine, batch_id, "api.match_city_fuzzy_override", "api_ods", "ods.city_ibge_match") as run, engine.begin() as conn:
        pairs = conn.execute(text("SELECT p.state_code, p.city, p.zips FROM ods.v_geo_city_pair p "
                                  "LEFT JOIN ods.city_ibge_match m USING (state_code, city) WHERE m.city IS NULL")).all()
        run.rows_read = len(pairs)
        mun = conn.execute(text("SELECT state_code, name_key, ibge_code FROM ods.ibge_municipio")).all()
        by_state: dict[str, list[tuple[str, int]]] = {}
        for st, key, code in mun:
            by_state.setdefault(st, []).append((key, code))
        valid = {code: st for st, _, code in mun}

        # tier 3: fuzzy
        inserted, left = [], []
        for st, city, zips in pairs:
            hit = fuzzy_pick(city, by_state.get(st, []))
            (inserted.append((st, city, hit[0], "fuzzy", hit[1])) if hit else left.append((st, city, zips)))

        # tier 4: hand-checked overrides; each must point to an existing municipality of the same state
        overrides = {}
        if OVERRIDE_CSV.exists():
            with OVERRIDE_CSV.open(encoding="utf-8", newline="") as fh:
                for r in csv.DictReader(fh):
                    code = int(r["ibge_code"])
                    if valid.get(code) != r["state_code"]:
                        raise ValueError(f"city_ibge_override.csv: {r['city']} -> {code} is not a municipality of {r['state_code']}")
                    overrides[(r["state_code"], r["city"])] = code
        still = []
        for st, city, zips in left:
            if (st, city) in overrides:
                inserted.append((st, city, overrides[(st, city)], "override", 100.0))
            else:
                still.append((st, city, zips))
        for st, city, code, method, score in inserted:
            conn.execute(text("INSERT INTO ods.city_ibge_match (state_code, city, ibge_code, method, score, etl_batch_id) "
                              "VALUES (:s, :c, :i, :m, :sc, :b)"), {"s": st, "c": city, "i": code, "m": method, "sc": score, "b": batch_id})
        run.rows_inserted = len(inserted)

        # statistics after every tier (recomputed over the full set of pairs)
        conn.execute(text("DELETE FROM etl_log.api_match_stat WHERE batch_id = :b"), {"b": batch_id})
        conn.execute(text("INSERT INTO etl_log.api_match_stat (batch_id, method, city_pairs, zips) "
                          "SELECT :b, coalesce(m.method, 'unmatched'), count(*), sum(p.zips) FROM ods.v_geo_city_pair p "
                          "LEFT JOIN ods.city_ibge_match m USING (state_code, city) GROUP BY 2"), {"b": batch_id})
        stats = {r[0]: {"pairs": r[1], "zips": r[2]} for r in conn.execute(
            text("SELECT method, city_pairs, zips FROM etl_log.api_match_stat WHERE batch_id = :b"), {"b": batch_id})}
        # the unmatched pairs are recomputed on every run: keep only the latest list, so the monitoring totals do not grow with every batch
        conn.execute(text("DELETE FROM etl_log.rejected_rows WHERE job_name = 'api.match_city_unmatched'"))
    if still:
        with job_run(engine, batch_id, "api.match_city_unmatched", "api_ods", "ods.city_ibge_match") as r:
            r.log_rejected("ods.v_geo_city_pair", "city not matched to an IBGE municipality (no exact, normalized, fuzzy or override match; often a district or neighbourhood)",
                           pd.DataFrame(still, columns=["state_code", "city", "zips"]))
    return stats
