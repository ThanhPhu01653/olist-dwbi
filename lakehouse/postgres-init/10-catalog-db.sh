#!/bin/sh
# Creates the database used by the Iceberg REST catalog (durable backend). Runs once, on first start of the data volume.
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres -c "CREATE DATABASE \"${LH_CATALOG_DB:-iceberg_catalog}\""
