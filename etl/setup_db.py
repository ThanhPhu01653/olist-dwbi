"""Create the databases and run sql/00_init + sql/10_source. Idempotent.

    python -m etl.setup_db            # create olist_dw and olist_full, run init + source DDL
    python -m etl.setup_db --check    # only test the connection and the available extensions
"""
from __future__ import annotations

import argparse
import sys

import psycopg2
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from . import config
from .db import get_engine

SOURCE_FOLDERS = ["00_init", "10_source"]                      # every database
WAREHOUSE_FOLDERS = SOURCE_FOLDERS + ["20_staging", "30_ods", "40_dw", "50_mart", "70_geo"]  # main warehouse database only
OPTIONAL_MARK = "-- setup: optional"


def check_environment() -> None:
    """Test the connection to the maintenance DB and that the unaccent extension can be created."""
    try:
        engine = get_engine("postgres")
        with engine.connect() as conn:
            version = conn.execute(text("SHOW server_version")).scalar_one()
            is_super = conn.execute(text("SELECT rolsuper FROM pg_roles WHERE rolname = current_user")).scalar_one()
            can_create_db = conn.execute(
                text("SELECT rolcreatedb OR rolsuper FROM pg_roles WHERE rolname = current_user")
            ).scalar_one()
            available = {
                r[0]: r[1]
                for r in conn.execute(
                    text("SELECT name, default_version FROM pg_available_extensions WHERE name = 'unaccent'")
                )
            }
    except OperationalError as exc:
        reason = str(exc.orig).strip().splitlines()[0] if exc.orig else str(exc)
        sys.exit(
            f"Cannot connect to PostgreSQL at {config.DB_HOST}:{config.DB_PORT} as '{config.DB_USER}'.\n"
            f"  -> {reason}\n"
            "Check that the PostgreSQL service is running and that DB_HOST/DB_PORT/DB_USER/DB_PASSWORD in .env are right."
        )
    print(f"Connected: PostgreSQL {version} at {config.DB_HOST}:{config.DB_PORT} as '{config.DB_USER}' "
          f"(superuser={is_super}, can create databases={can_create_db})")
    print("  extension unaccent : " + (f"available (v{available['unaccent']})" if "unaccent" in available else "NOT available"))
    if not can_create_db:
        sys.exit("This role cannot create databases. Use a superuser (e.g. postgres) in .env.")
    if "unaccent" not in available:
        sys.exit("The 'unaccent' extension is missing (it ships with PostgreSQL contrib). Reinstall PostgreSQL with default components.")


def create_database_if_missing(name: str) -> None:
    engine = get_engine("postgres", isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        exists = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": name}).first()
        if exists:
            print(f"Database {name}: already exists")
            return
        # Identifier cannot be a bind parameter; the name comes from our own .env.
        conn.execute(text(f'CREATE DATABASE "{name}" ENCODING \'UTF8\' TEMPLATE template0'))
        print(f"Database {name}: created")
    engine.dispose()


def run_sql_files(database: str, folders: list[str]) -> None:
    engine = get_engine(database)
    for folder in folders:
        if not (config.SQL_DIR / folder).exists():
            continue
        for path in sorted((config.SQL_DIR / folder).glob("*.sql")):
            sql = path.read_text(encoding="utf-8")
            optional = OPTIONAL_MARK in sql
            rel = f"{folder}/{path.name}"
            raw = engine.raw_connection()  # plain psycopg2: no parameter parsing, so '%' in SQL is safe
            try:
                with raw.cursor() as cur:
                    cur.execute(sql)
                raw.commit()
                print(f"  [{database}] {rel}: ok")
            except psycopg2.Error as exc:
                raw.rollback()
                if not optional:
                    raise
                reason = (exc.pgerror or str(exc)).strip().splitlines()[0]
                print(f"  [{database}] {rel}: SKIPPED (optional) -> {reason}")
            finally:
                raw.close()
    engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="only check connection and extensions")
    parser.add_argument("--database", action="append", help="database to set up (repeatable); default: DB_NAME and DB_NAME_FULL")
    args = parser.parse_args()

    check_environment()
    if args.check:
        return
    for name in args.database or [config.DB_NAME, config.DB_NAME_FULL]:
        create_database_if_missing(name)
        run_sql_files(name, WAREHOUSE_FOLDERS if name == config.DB_NAME else SOURCE_FOLDERS)
    print("Setup done.")


if __name__ == "__main__":
    main()
