"""Helpers shared by the Spark jobs of the Lakehouse: the cleaning functions of the warehouse ODS (sql/30_ods/020_ods_procs.sql) and the city matching
(api_ingest/match.py). Pure Python parts are importable without Spark so that tests can use them."""
import re
import unicodedata

from pyspark.sql import functions as F, types as T


def py_unaccent(s):
    """Like PostgreSQL unaccent: removes accents (canonical decomposition, NFD) but leaves characters such as the ordinal indicator alone."""
    if s is None:
        return None
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def py_name_key(s):
    """ods.name_key: lower case, no accents, every run of non-alphanumeric characters becomes one space, trimmed; empty -> None."""
    if s is None:
        return None
    k = re.sub(r"[^a-z0-9]+", " ", py_unaccent(s).lower()).strip()
    return k or None


def lcs_len(a: str, b: str) -> int:
    prev = [0] * (len(b) + 1)
    for ca in a:
        cur = [0]
        for j, cb in enumerate(b, 1):
            cur.append(prev[j - 1] + 1 if ca == cb else max(prev[j], cur[j - 1]))
        prev = cur
    return prev[-1]


def indel_ratio(a: str, b: str) -> float:
    """rapidfuzz fuzz.ratio: normalised Indel similarity, 0..100 (= 200 * LCS / (len a + len b))."""
    if not a and not b:
        return 100.0
    return 200.0 * lcs_len(a, b) / (len(a) + len(b))


FUZZY_THRESHOLD, FUZZY_GAP = 95, 10


def fuzzy_pick(city, candidates, threshold=FUZZY_THRESHOLD, gap=FUZZY_GAP):
    """candidates: [(name_key, ibge_code)] of one state. (ibge_code, score) when exactly one candidate qualifies, else None (same rule as api_ingest/match.py)."""
    if not candidates:
        return None
    scored = sorted(((indel_ratio(city, k), i) for i, (k, _) in enumerate(candidates)), key=lambda x: (-x[0], x[1]))[:2]
    best = scored[0]
    second = scored[1][0] if len(scored) > 1 else 0
    if best[0] >= threshold and best[0] - second >= gap:
        return candidates[best[1]][1], round(best[0], 1)
    return None


unaccent_udf = F.udf(py_unaccent, T.StringType())
name_key = F.udf(py_name_key, T.StringType())
clean_zip = lambda c: F.when(F.regexp_replace(F.coalesce(c, F.lit("")), r"\D", "") == "", F.lit(None)).otherwise(F.substring(F.lpad(F.regexp_replace(c, r"\D", ""), 5, "0"), 1, 5))
clean_city = lambda c: F.when(F.trim(unaccent_udf(F.lower(F.trim(c)))) == "", F.lit(None)).otherwise(F.lower(unaccent_udf(F.trim(c))))
clean_state = lambda c: F.when(F.substring(F.upper(F.trim(c)), 1, 2) == "", F.lit(None)).otherwise(F.substring(F.upper(F.trim(c)), 1, 2))
