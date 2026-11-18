"""Collector: call the APIs, write the raw JSON into the landing zone, log every call in etl_log.api_call.

Landing zone:  data/raw/api/<source>/<run date>/<name>.json  (the response body, byte for byte)  +  manifest.json (one entry per call:
url, called_at, HTTP status, records, bytes, sha256, seconds, attempts). Re-running on the same day overwrites the same files, so a re-run never
duplicates anything; Banco Central series are incremental (only dates after the watermark etl_log.watermark are requested).
"""
from __future__ import annotations

import json
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Engine

from . import config
from .http import Client, Response


class SourceError(RuntimeError):
    """A source could not be collected; the other sources are still collected."""


def count_records(name: str, body: object) -> int:
    if isinstance(body, list):
        if body and isinstance(body[0], dict) and "resultados" in body[0]:          # IBGE SIDRA: list of variables
            return sum(len(r["series"]) for v in body for r in v["resultados"])
        return len(body)
    if isinstance(body, dict):
        if "daily" in body:                                                          # Open-Meteo archive
            return len(body["daily"].get("time", []))
        if "results" in body:                                                        # Open-Meteo geocoding
            return len(body["results"])
        if "variaveis" in body:                                                      # IBGE aggregate metadata
            return len(body["variaveis"])
    return 1


class Collector:
    def __init__(self, engine: Engine | None, batch_id: int | None, client: Client | None = None, run_date: str | None = None,
                 landing_root: Path | None = None):
        self.engine, self.batch_id = engine, batch_id
        self.client = client or Client()
        self.run_date = run_date or date.today().isoformat()
        self.root = landing_root or config.LANDING_DIR
        self.calls: list[dict] = []

    # ---------------------------------------------------------------- one call
    def call(self, source: str, name: str, url: str, params: dict | None = None, required: bool = True) -> tuple[Response, object | None]:
        folder = self.root / source / self.run_date
        called_at = datetime.now(timezone.utc)
        resp = self.client.get(url, params)
        body, records, path, error = None, None, None, resp.error
        if resp.ok:
            try:
                body = json.loads(resp.content)
                records = count_records(name, body)
                folder.mkdir(parents=True, exist_ok=True)
                path = folder / f"{name}.json"
                path.write_bytes(resp.content)
            except ValueError as exc:
                error = f"invalid JSON: {exc}"
        entry = {"source": source, "name": name, "url": resp.url, "called_at": called_at.isoformat(timespec="seconds"), "http_status": resp.status,
                 "records": records, "bytes": len(resp.content), "sha256": resp.sha256 if resp.content else None, "seconds": resp.seconds,
                 "attempts": resp.attempts, "file": path.name if path else None, "error": error}
        self.calls.append(entry)
        self._manifest(folder, entry)
        self._log(entry, self._rel(path))
        if error and required:
            raise SourceError(f"{source}/{name}: {error}")
        return resp, body

    @staticmethod
    def _rel(path: Path | None) -> str | None:
        if path is None:
            return None
        try:
            return str(path.relative_to(config.ROOT)).replace("\\", "/")
        except ValueError:                      # landing root outside the repo (tests)
            return str(path).replace("\\", "/")

    def _manifest(self, folder: Path, entry: dict) -> None:
        folder.mkdir(parents=True, exist_ok=True)
        mpath = folder / "manifest.json"
        items = json.loads(mpath.read_text(encoding="utf-8")) if mpath.exists() else []
        items = [e for e in items if e["name"] != entry["name"]] + [entry]
        mpath.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")

    def _log(self, e: dict, rel_path: str | None) -> None:
        if self.engine is None:
            return
        with self.engine.begin() as conn:
            conn.execute(text(
                "INSERT INTO etl_log.api_call (batch_id, source, name, url, called_at, http_status, records, bytes, sha256, seconds, attempts, landing_path, error) "
                "VALUES (:b, :s, :n, :u, :t, :h, :r, :y, :x, :sec, :a, :p, :err)"),
                {"b": self.batch_id, "s": e["source"], "n": e["name"], "u": e["url"], "t": e["called_at"], "h": e["http_status"], "r": e["records"],
                 "y": e["bytes"], "x": e["sha256"], "sec": e["seconds"], "a": e["attempts"], "p": rel_path, "err": e["error"]})

    # ---------------------------------------------------------------- watermark (incremental Banco Central series)
    def watermark(self, key: str) -> date | None:
        if self.engine is None:
            return None
        with self.engine.connect() as conn:
            v = conn.execute(text("SELECT last_value FROM etl_log.watermark WHERE source_table = :k"), {"k": key}).scalar()
        return v.date() if v else None

    def set_watermark(self, key: str, d: date) -> None:
        if self.engine is None:
            return
        with self.engine.begin() as conn:
            conn.execute(text("INSERT INTO etl_log.watermark (source_table, last_value) VALUES (:k, :v) "
                              "ON CONFLICT (source_table) DO UPDATE SET last_value = EXCLUDED.last_value, updated_at = now()"), {"k": key, "v": d})

    # ---------------------------------------------------------------- sources
    def collect_ibge(self) -> None:
        loc, agg = config.IBGE_LOCALIDADES, config.IBGE_AGREGADOS
        self.call("ibge", "estados", f"{loc}/estados")
        self.call("ibge", "municipios", f"{loc}/municipios")
        # metadata first: the aggregate / variable codes are checked against the API itself (never guessed)
        _, meta_pop = self.call("ibge", f"metadados_{config.POPULATION_AGGREGATE}", f"{agg}/{config.POPULATION_AGGREGATE}/metadados")
        _, meta_gdp = self.call("ibge", f"metadados_{config.GDP_AGGREGATE}", f"{agg}/{config.GDP_AGGREGATE}/metadados")
        _, meta_ipca = self.call("ibge", f"metadados_{config.IPCA_AGGREGATE}", f"{agg}/{config.IPCA_AGGREGATE}/metadados")
        for meta, var, unit_part in ((meta_pop, config.POPULATION_VARIABLE, "Pessoas"), (meta_gdp, config.GDP_VARIABLE, "Mil Reais"),
                                     (meta_ipca, 63, "%")):
            found = {v["id"]: v["unidade"] for v in meta["variaveis"]}
            if found.get(var) != unit_part:
                raise SourceError(f"IBGE metadata: variable {var} has unit {found.get(var)!r}, expected {unit_part!r}")
        years = "|".join(str(y) for y in config.YEARS)
        self.call("ibge", "populacao", f"{agg}/{config.POPULATION_AGGREGATE}/periodos/{years}/variaveis/{config.POPULATION_VARIABLE}?localidades=N6[all]")
        self.call("ibge", "pib", f"{agg}/{config.GDP_AGGREGATE}/periodos/{years}/variaveis/{config.GDP_VARIABLE}?localidades=N6[all]")
        self.call("ibge", "ipca_ibge", f"{agg}/{config.IPCA_AGGREGATE}/periodos/201601-202012/variaveis/63|2266?localidades=N1[all]")

    def collect_bcb(self) -> None:
        last = date.fromisoformat(config.BCB_LAST_DATE)
        for code, first in ((config.SGS_USD_SELL, config.BCB_FIRST_DATE), (config.SGS_IPCA_MONTHLY, "2016-01-01")):
            key = f"api.bcb_sgs_{code}"
            wm = self.watermark(key)
            start = max(date.fromisoformat(first), wm + timedelta(days=1)) if wm else date.fromisoformat(first)
            if start > last:
                continue                                        # nothing new to ask for
            url = config.BCB_SGS.format(code=code)
            params = {"formato": "json", "dataInicial": start.strftime("%d/%m/%Y"), "dataFinal": last.strftime("%d/%m/%Y")}
            resp, body = self.call("bcb", f"sgs_{code}_{start:%Y%m%d}_{last:%Y%m%d}", url, params)
            if body:
                newest = max(datetime.strptime(r["data"], "%d/%m/%Y").date() for r in body)
                self.set_watermark(key, newest)

    def collect_holidays(self) -> None:
        for y in config.HOLIDAY_YEARS:
            self.call("holidays", f"feriados_{y}", config.BRASILAPI_HOLIDAYS.format(year=y))

    def collect_weather(self) -> None:
        for uf, city in config.CAPITALS.items():
            _, geo = self.call("weather", f"geocode_{uf}", config.OPEN_METEO_GEOCODING,
                               {"name": city, "country_code": "BR", "count": 10, "language": "pt", "format": "json"})
            hit = next((r for r in geo.get("results", []) if r.get("country_code") == "BR" and r.get("feature_code") in ("PPLA", "PPLC")), None)  # seat of a state / federal capital
            if hit is None:
                raise SourceError(f"weather/geocode_{uf}: no result for {city}")
            self.call("weather", f"archive_{uf}", config.OPEN_METEO_ARCHIVE,
                      {"latitude": hit["latitude"], "longitude": hit["longitude"], "start_date": config.WEATHER_FIRST_DATE,
                       "end_date": config.WEATHER_LAST_DATE, "daily": "precipitation_sum", "timezone": "America/Sao_Paulo"})

    def collect(self, sources: list[str]) -> dict[str, str | None]:
        """Collect each source; return {source: error message or None}. A failing source never stops the others."""
        outcome: dict[str, str | None] = {}
        for s in sources:
            t0 = time.perf_counter()
            try:
                getattr(self, f"collect_{s}")()
                outcome[s] = None
            except Exception as exc:                            # noqa: BLE001 - report and go on with the next source
                outcome[s] = f"{type(exc).__name__}: {str(exc)[:300]}"
            self.last_seconds = {**getattr(self, "last_seconds", {}), s: round(time.perf_counter() - t0, 1)}
        return outcome
