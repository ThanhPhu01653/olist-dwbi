"""API staging -> ODS: typed tables (IBGE, USD/BRL, IPCA, holidays, weather) and the city -> IBGE municipality match."""
from __future__ import annotations

from sqlalchemy.engine import Engine

from etl.procs import call_procedures

from .match import match_cities

API_ODS_PROCS = [
    ("ods.load_api_ibge", "ods.ibge_municipio / ibge_population / ibge_gdp"),
    ("ods.load_api_fx", "ods.fx_usd_brl"),
    ("ods.load_api_ipca", "ods.ipca_month"),
    ("ods.load_api_holidays", "ods.holiday_official"),
    ("ods.load_api_weather", "ods.weather_daily"),
]


def run_ods(engine: Engine, batch_id: int) -> dict:
    res = call_procedures(engine, batch_id, "api_ods", API_ODS_PROCS)
    stats = match_cities(engine, batch_id)
    return {"procs": {r["proc"]: {"read": r["read"], "inserted": r["inserted"], "rejected": r["rejected"]} for r in res}, "city_match": stats}
