"""Endpoints, series codes and limits of the API collector. Codes were checked against the metadata of each API (see docs/THU_THAP_API.md)."""
from __future__ import annotations

from pathlib import Path

from etl import config as etl_config

ROOT = etl_config.ROOT
LANDING_DIR = ROOT / "data" / "raw" / "api"          # not committed (data/raw/ is in .gitignore)

# Generic client name: never a personal e-mail address.
USER_AGENT = "olist-dwbi-student-project/1.0 (university coursework; public data only)"
TIMEOUT = (10, 120)                                   # connect, read (seconds)
MAX_ATTEMPTS = 5
BACKOFF_SECONDS = 1.5                                 # waits 1.5, 3, 6, 12 s between attempts
MIN_INTERVAL = {                                      # minimum seconds between two calls to the same host
    "servicodados.ibge.gov.br": 0.5,
    "api.bcb.gov.br": 1.0,
    "brasilapi.com.br": 0.5,
    "geocoding-api.open-meteo.com": 1.0,
    "archive-api.open-meteo.com": 1.5,
}

IBGE_LOCALIDADES = "https://servicodados.ibge.gov.br/api/v1/localidades"
IBGE_AGREGADOS = "https://servicodados.ibge.gov.br/api/v3/agregados"
POPULATION_AGGREGATE, POPULATION_VARIABLE = 6579, 9324        # "Estimativas de populacao": variable "Populacao residente estimada" (people)
GDP_AGGREGATE, GDP_VARIABLE = 5938, 37                        # "PIB dos Municipios": variable "PIB a precos correntes" (thousand BRL)
IPCA_AGGREGATE = 1737                                         # IPCA series; variable 63 = monthly change (%), 2266 = index (Dec 1993 = 100)
YEARS = (2016, 2017, 2018)                                    # years covered by the Olist orders

BCB_SGS = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados"
SGS_USD_SELL = 1                                              # "Taxa de cambio - Livre - Dolar americano (venda) - diario" (BRL per USD)
SGS_IPCA_MONTHLY = 433                                        # IPCA monthly change (%): identical to IBGE aggregate 1737 variable 63 (checked)
BCB_FIRST_DATE = "2015-12-01"                                 # one month before dim_date starts, so 2016-01-01 can use the last 2015 rate
BCB_LAST_DATE = "2020-12-31"                                  # dim_date ends here; the BCB limits date-range queries to 10 years

BRASILAPI_HOLIDAYS = "https://brasilapi.com.br/api/feriados/v1/{year}"
HOLIDAY_YEARS = range(2016, 2021)

OPEN_METEO_GEOCODING = "https://geocoding-api.open-meteo.com/v1/search"
OPEN_METEO_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
WEATHER_FIRST_DATE, WEATHER_LAST_DATE = "2016-01-01", "2018-12-31"

# State capitals (the weather station of each state). The coordinates come from the geocoding API, not from this list.
CAPITALS = {
    "AC": "Rio Branco", "AL": "Maceió", "AP": "Macapá", "AM": "Manaus", "BA": "Salvador", "CE": "Fortaleza", "DF": "Brasília",
    "ES": "Vitória", "GO": "Goiânia", "MA": "São Luís", "MT": "Cuiabá", "MS": "Campo Grande", "MG": "Belo Horizonte", "PA": "Belém",
    "PB": "João Pessoa", "PR": "Curitiba", "PE": "Recife", "PI": "Teresina", "RJ": "Rio de Janeiro", "RN": "Natal", "RS": "Porto Alegre",
    "RO": "Porto Velho", "RR": "Boa Vista", "SC": "Florianópolis", "SP": "São Paulo", "SE": "Aracaju", "TO": "Palmas",
}

SOURCES = ["ibge", "bcb", "holidays", "weather"]


def landing_dir(source: str, run_date: str) -> Path:
    return LANDING_DIR / source / run_date
