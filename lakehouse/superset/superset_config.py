"""Superset configuration for the lakehouse demo profile (values come from the environment, nothing is hardcoded)."""
import os

SECRET_KEY = os.environ["SUPERSET_SECRET_KEY"]
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://{u}:{p}@pg:5432/superset".format(u=os.environ["LH_PG_USER"], p=os.environ["LH_PG_PASSWORD"])
ROW_LIMIT = 50000
SUPERSET_WEBSERVER_TIMEOUT = 120
# Vietnamese number style: 13.494.400,74
D3_FORMAT = {"decimal": ",", "thousands": ".", "grouping": [3], "currency": ["", " BRL"]}
