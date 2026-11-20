"""Bronze for the API sources: read the raw JSON of the landing zone (s3a://lakehouse/landing/api/<source>/<run date>/*.json) as text and keep it unchanged.

    docker exec lh-spark /opt/spark/bin/spark-submit --master local[2] --properties-file /opt/lakehouse/spark/spark-defaults.conf /opt/lakehouse/spark/bronze_api.py

One table per source: bronze.api_ibge, api_bcb, api_holidays, api_weather. One row per file (schema-on-read: the JSON stays a string in `payload`;
Silver parses it). manifest.json of every run is kept as a row too. Append only; a file already in the table (same source, run_date, file_name,
sha256) is skipped, so re-running adds nothing.
"""
import re

from pyspark.sql import SparkSession, functions as F

SOURCES = ["ibge", "bcb", "holidays", "weather"]
spark = SparkSession.builder.appName("bronze_api").getOrCreate()
spark.sql("CREATE NAMESPACE IF NOT EXISTS bronze")
total = {}
for src in SOURCES:
    table = f"bronze.api_{src}"
    spark.sql(f"""CREATE TABLE IF NOT EXISTS {table} (source string, run_date string, file_name string, payload string,
                  payload_bytes bigint, sha256 string, ingested_at timestamp) USING iceberg""")
    raw = (spark.read.text(f"s3a://lakehouse/landing/api/{src}/*/*.json", wholetext=True)
           .withColumn("path", F.input_file_name()))
    new = raw.select(
        F.lit(src).alias("source"),
        F.regexp_extract("path", r"/landing/api/[^/]+/([^/]+)/[^/]+$", 1).alias("run_date"),
        F.regexp_extract("path", r"/([^/]+)$", 1).alias("file_name"),
        F.col("value").alias("payload"),
        F.length(F.encode("value", "UTF-8")).cast("long").alias("payload_bytes"),
        F.sha2(F.col("value"), 256).alias("sha256"),
        F.current_timestamp().alias("ingested_at"))
    have = spark.table(table).select("source", "run_date", "file_name", "sha256")
    fresh = new.join(have, ["source", "run_date", "file_name", "sha256"], "left_anti")
    n = fresh.count()
    if n:
        fresh.writeTo(table).append()
    total[src] = (n, spark.table(table).count())
for k, (n, t) in total.items():
    print(f"BRONZE_API {k}: appended {n}, table now {t} rows")
