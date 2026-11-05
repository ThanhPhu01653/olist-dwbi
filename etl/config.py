"""Project configuration, read from the environment / .env file."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

SQL_DIR = ROOT / "sql"
RAW_ECOMMERCE_DIR = ROOT / "data" / "raw" / "ecommerce"
RAW_MARKETING_DIR = ROOT / "data" / "raw" / "marketing"

# Initial load keeps source records up to this date (DW_DESIGN.md section 12).
INITIAL_CUTOFF = "2017-12-31"


def _get(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value == "":
        # CLI project: exit with a readable message instead of a traceback.
        raise SystemExit(
            f"Missing {name}. Copy .env.example to .env (in {ROOT}) and fill in the PostgreSQL password."
        )
    return value


DB_HOST = _get("DB_HOST", "localhost")
DB_PORT = int(_get("DB_PORT", "5432"))
DB_USER = _get("DB_USER", "postgres")
DB_NAME = _get("DB_NAME", "olist_dw")
DB_NAME_FULL = _get("DB_NAME_FULL", "olist_full")


def db_password() -> str:
    # Read lazily so that importing the package never fails when only paths are needed.
    return _get("DB_PASSWORD")
