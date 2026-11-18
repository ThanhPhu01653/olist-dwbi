"""Landing zone (raw JSON) -> staging schema api (stg_api_*). Parsers are pure functions; loading is TRUNCATE+COPY (full-refresh sources) or
upsert on the natural key (incremental sources), so running it twice never duplicates a row."""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path

from sqlalchemy.engine import Engine

from etl.log import job_run

from . import config


# ----------------------------------------------------------------------------- parsers (pure)
def parse_estados(body: list) -> list[tuple]:
    return [(e["id"], e["sigla"], e["nome"], e["regiao"]["id"], e["regiao"]["sigla"], e["regiao"]["nome"]) for e in body]


def parse_municipios(body: list) -> list[tuple]:
    rows = []
    for m in body:
        mic = m.get("microrregiao") or {}
        mes = mic.get("mesorregiao") or {}
        imm = m.get("regiao-imediata") or {}
        inter = imm.get("regiao-intermediaria") or {}
        uf = (mes.get("UF") or inter.get("UF") or {})
        rows.append((m["id"], m["nome"], uf.get("id"), uf.get("sigla"), mic.get("id"), mic.get("nome"), mes.get("id"), mes.get("nome"),
                     imm.get("id"), imm.get("nome"), inter.get("id"), inter.get("nome")))
    return rows


def parse_sidra(body: list) -> list[tuple]:
    """SIDRA aggregate response -> (ibge_code, year, raw value)."""
    out = []
    for var in body:
        for res in var["resultados"]:
            for s in res["series"]:
                code = int(s["localidade"]["id"])
                for period, value in s["serie"].items():
                    out.append((code, int(period), value))
    return out


def parse_ipca_ibge(body: list) -> list[tuple]:
    by: dict[str, dict] = {}
    for var in body:
        key = "var_raw" if var["id"] == "63" else "index_raw"
        for s in var["resultados"][0]["series"]:
            for period, value in s["serie"].items():
                by.setdefault(period, {})[key] = value
    return [(p, v.get("var_raw"), v.get("index_raw")) for p, v in sorted(by.items())]


def parse_sgs(code: int, body: list) -> list[tuple]:
    from datetime import datetime
    return [(code, datetime.strptime(r["data"], "%d/%m/%Y").date(), r["valor"]) for r in body]


def parse_holidays(body: list) -> list[tuple]:
    return [(h["date"], h["name"], h.get("type")) for h in body]


def parse_station(uf: str, geo: dict) -> tuple:
    hit = next(r for r in geo["results"] if r.get("country_code") == "BR" and r.get("feature_code") in ("PPLA", "PPLC"))
    return (uf, hit["name"], hit["latitude"], hit["longitude"])


def parse_weather(uf: str, body: dict) -> list[tuple]:
    d = body["daily"]
    return [(uf, t, None if v is None else str(v)) for t, v in zip(d["time"], d["precipitation_sum"])]


# ----------------------------------------------------------------------------- landing zone readers
def run_dirs(source: str, root: Path | None = None) -> list[Path]:
    base = (root or config.LANDING_DIR) / source
    return sorted(p for p in base.iterdir() if p.is_dir()) if base.exists() else []


def latest_file(source: str, name: str, root: Path | None = None) -> Path | None:
    for d in reversed(run_dirs(source, root)):
        if (d / f"{name}.json").exists():
            return d / f"{name}.json"
    return None


def read_json(path: Path):
    return json.loads(path.read_bytes())


# ----------------------------------------------------------------------------- loading
def _copy_replace(cur, table: str, columns: list[str], rows: list[tuple], batch_id: int, truncate: bool, key: list[str]) -> int:
    cols = list(columns) + ["load_batch_id"]
    cur.execute(f"CREATE TEMP TABLE tmp_stage (LIKE {table} INCLUDING DEFAULTS) ON COMMIT DROP")
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    for r in rows:
        w.writerow(["" if v is None else v for v in (*r, batch_id)])        # None -> empty field -> NULL (pandas would turn int columns into floats)
    buf.seek(0)
    cur.copy_expert(f"COPY tmp_stage ({', '.join(cols)}) FROM STDIN WITH (FORMAT csv)", buf)
    if truncate:
        cur.execute(f"TRUNCATE {table}")
    sets = ", ".join(f"{c} = EXCLUDED.{c}" for c in cols if c not in key)
    cur.execute(f"INSERT INTO {table} ({', '.join(cols)}) SELECT {', '.join(cols)} FROM tmp_stage "
                f"ON CONFLICT ({', '.join(key)}) DO UPDATE SET {sets}, loaded_at = now()")
    n = cur.rowcount
    cur.execute("DROP TABLE tmp_stage")
    return n


def stage_all(engine: Engine, batch_id: int, root: Path | None = None) -> dict[str, int]:
    """Load every staging table from the landing zone. Returns {table: rows}. Sources with no landed file are skipped."""
    plan: list[tuple[str, str, list[str], list[tuple], bool, list[str]]] = []   # (job, table, columns, rows, truncate, key)

    def add(job, table, columns, rows, truncate, key):
        if rows:
            plan.append((job, table, columns, rows, truncate, key))

    f = latest_file("ibge", "estados", root)
    if f:
        add("api.stage_ibge_estado", "api.stg_api_ibge_estado", ["ibge_code", "sigla", "nome", "regiao_code", "regiao_sigla", "regiao_nome"],
            parse_estados(read_json(f)), True, ["ibge_code"])
    f = latest_file("ibge", "municipios", root)
    if f:
        add("api.stage_ibge_municipio", "api.stg_api_ibge_municipio",
            ["ibge_code", "nome", "uf_code", "uf_sigla", "microrregiao_code", "microrregiao_nome", "mesorregiao_code", "mesorregiao_nome",
             "imediata_code", "imediata_nome", "intermediaria_code", "intermediaria_nome"], parse_municipios(read_json(f)), True, ["ibge_code"])
    for name, table in (("populacao", "api.stg_api_ibge_populacao"), ("pib", "api.stg_api_ibge_pib")):
        f = latest_file("ibge", name, root)
        if f:
            add(f"api.stage_ibge_{name}", table, ["ibge_code", "year", "value_raw"], parse_sidra(read_json(f)), True, ["ibge_code", "year"])
    f = latest_file("ibge", "ipca_ibge", root)
    if f:
        add("api.stage_ibge_ipca", "api.stg_api_ibge_ipca", ["period", "var_raw", "index_raw"], parse_ipca_ibge(read_json(f)), True, ["period"])

    sgs: list[tuple] = []
    for d in run_dirs("bcb", root):
        for p in sorted(d.glob("sgs_*.json")):
            code = int(p.stem.split("_")[1])
            sgs += parse_sgs(code, read_json(p))
    add("api.stage_bcb_serie", "api.stg_api_bcb_serie", ["series_code", "ref_date", "value_raw"], sgs, False, ["series_code", "ref_date"])

    hol: list[tuple] = []
    for y in config.HOLIDAY_YEARS:
        f = latest_file("holidays", f"feriados_{y}", root)
        if f:
            hol += parse_holidays(read_json(f))
    add("api.stage_holiday", "api.stg_api_holiday", ["holiday_date", "name", "type"], hol, True, ["holiday_date", "name"])

    stations, daily = [], []
    for uf in config.CAPITALS:
        g, a = latest_file("weather", f"geocode_{uf}", root), latest_file("weather", f"archive_{uf}", root)
        if g and a:
            stations.append(parse_station(uf, read_json(g)))
            daily += parse_weather(uf, read_json(a))
    add("api.stage_weather_station", "api.stg_api_weather_station", ["state_code", "city", "latitude", "longitude"], stations, True, ["state_code"])
    add("api.stage_weather_daily", "api.stg_api_weather_daily", ["state_code", "obs_date", "precip_raw"], daily, True, ["state_code", "obs_date"])

    counts: dict[str, int] = {}
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        for job, table, cols, rows, truncate, key in plan:
            with job_run(engine, batch_id, job, "api", table) as run:
                run.rows_read = len(rows)
                run.rows_inserted = counts[table] = _copy_replace(cur, table, cols, rows, batch_id, truncate, key)
        raw.commit()
    except BaseException:
        raw.rollback()
        raise
    finally:
        raw.close()
    return counts


def restore_log(engine: Engine, batch_id: int, root: Path | None = None) -> dict[str, int]:
    """After a rebuild etl_log is empty but the landing zone still has the manifests: put the calls back into etl_log.api_call (once each)
    and the Banco Central watermarks back into etl_log.watermark (newest date in staging), so history and incremental fetching survive a rebuild."""
    from sqlalchemy import text
    base = root or config.LANDING_DIR
    added = 0
    with engine.begin() as conn:
        for mf in sorted(base.glob("*/*/manifest.json")):
            for e in read_json(mf):
                exists = conn.execute(text("SELECT 1 FROM etl_log.api_call WHERE url = :u AND called_at = :t"), {"u": e["url"], "t": e["called_at"]}).first()
                if exists:
                    continue
                conn.execute(text(
                    "INSERT INTO etl_log.api_call (batch_id, source, name, url, called_at, http_status, records, bytes, sha256, seconds, attempts, landing_path, error) "
                    "VALUES (:b, :s, :n, :u, :t, :h, :r, :y, :x, :sec, :a, :p, :err)"),
                    {"b": batch_id, "s": e["source"], "n": e["name"], "u": e["url"], "t": e["called_at"], "h": e["http_status"], "r": e["records"], "y": e["bytes"],
                     "x": e["sha256"], "sec": e["seconds"], "a": e["attempts"], "p": f"data/raw/api/{e['source']}/{mf.parent.name}/{e['file']}" if e.get("file") else None,
                     "err": e["error"]})
                added += 1
        conn.execute(text("INSERT INTO etl_log.watermark (source_table, last_value) SELECT 'api.bcb_sgs_' || series_code, max(ref_date) FROM api.stg_api_bcb_serie GROUP BY series_code "
                          "ON CONFLICT (source_table) DO UPDATE SET last_value = GREATEST(etl_log.watermark.last_value, EXCLUDED.last_value), updated_at = now()"))
    return {"api_call_restored": added}
