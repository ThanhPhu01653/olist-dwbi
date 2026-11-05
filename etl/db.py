"""Database connections (SQLAlchemy engine + raw psycopg2 for COPY)."""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine

from . import config


def make_url(database: str | None = None) -> URL:
    return URL.create(
        "postgresql+psycopg2",
        username=config.DB_USER,
        password=config.db_password(),
        host=config.DB_HOST,
        port=config.DB_PORT,
        database=database or config.DB_NAME,
    )


def get_engine(database: str | None = None, **kwargs) -> Engine:
    """SQLAlchemy engine for `database` (defaults to DB_NAME from .env)."""
    return create_engine(
        make_url(database),
        connect_args={"client_encoding": "utf8"},
        future=True,
        **kwargs,
    )
