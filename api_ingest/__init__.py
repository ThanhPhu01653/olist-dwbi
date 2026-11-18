"""P9: collect public data of Brazil from APIs (IBGE, Banco Central do Brasil, BrasilAPI, Open-Meteo) to enrich the warehouse.

    python -m api_ingest.run --source all|ibge|bcb|holidays|weather [--offline]

collector (this package) -> landing zone data/raw/api/<source>/<run date>/*.json (raw, verbatim) + manifest.json
-> staging schema api (stg_api_*) -> ODS (ods.ref_ibge_*, fx, ipca, holidays, city match) -> dw enrichment (dim_geography, dim_date, fact_state_year).
"""
