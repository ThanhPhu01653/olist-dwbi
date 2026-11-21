# Superset 4.1.2 + Trino driver and psycopg2 (metadata in PostgreSQL) (dashboards read the Gold layer through Trino as the read-only user bi_viewer)
FROM apache/superset:4.1.2
USER root
RUN pip install --no-cache-dir "trino[sqlalchemy]==0.333.0" psycopg2-binary
USER superset
