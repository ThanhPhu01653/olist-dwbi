"""Shared helpers of the Lakehouse scripts: read lakehouse/.env and build the environment that points the project's ETL code at the
Lakehouse source PostgreSQL (container, port 5433) instead of the warehouse database. olist_dw is never touched."""
from __future__ import annotations

import os
from pathlib import Path

LH = Path(__file__).resolve().parent.parent          # lakehouse/
ROOT = LH.parent


def load_env() -> dict[str, str]:
    f = LH / ".env"
    if not f.exists():
        raise SystemExit("lakehouse/.env not found: copy lakehouse/.env.example to lakehouse/.env")
    env: dict[str, str] = {}
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def source_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    """os.environ + DB_* variables of etl/config.py aimed at the source container. DB_NAME is left as in the project .env (olist_dw) on purpose:
    the Lakehouse source database is always passed with --database, and because it differs from DB_NAME setup_db creates only the source schemas there."""
    e = load_env()
    out = dict(os.environ)
    out.update({"DB_HOST": "127.0.0.1", "DB_PORT": e["LH_PG_PORT"], "DB_USER": e["LH_PG_USER"], "DB_PASSWORD": e["LH_PG_PASSWORD"]})
    out.update(extra or {})
    return out
