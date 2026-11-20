"""Spark Structured Streaming: Kafka (Debezium events) -> Bronze -> Silver, one application, micro-batches of --trigger-seconds.

    docker exec -d lh-spark /opt/spark/bin/spark-submit --master local[2] --properties-file /opt/lakehouse/spark/spark-defaults.conf \
        /opt/lakehouse/spark/stream_bronze_silver.py [--trigger-seconds 30] [--max-offsets 100000] [--available-now]

Bronze  (bronze.<schema>_<table>, append only): key, payload (the Debezium JSON), op (c/u/d/r), ts_ms, source_table, kafka_partition, kafka_offset,
        kafka_timestamp, ingested_at. Nothing is changed or dropped.
Silver  (silver.<table>): the cleaning rules of the warehouse ODS (sql/30_ods/020_ods_procs.sql) applied to the latest event of every key, written with
        MERGE on the primary key; an event only replaces a row when its ts_ms is not older (Debezium delivers at least once, replays must not duplicate).
        Rows that cannot be loaded go to silver.<table>_rejected with an error code (orphans are retried in every batch and leave the table when their
        parent has arrived). silver.order_status_history gets one row per status change of an order.
geolocation is kept in Bronze only here: its Silver table (one row per zip) is built by silver_batch.py from the whole Bronze table.
"""
import argparse
import threading
import unicodedata

from pyspark.sql import SparkSession, Window, functions as F, types as T

ap = argparse.ArgumentParser()
ap.add_argument("--trigger-seconds", type=int, default=30)
ap.add_argument("--max-offsets", type=int, default=100000, help="max Kafka events per micro-batch (bounds memory)")
ap.add_argument("--available-now", action="store_true", help="process what is in Kafka now, then stop (used by tests and catch-up)")
ap.add_argument("--debug-batches", type=int, default=0, help="debug: stop the query after this many batches (0 = no limit)")
ap.add_argument("--checkpoint", default="s3a://lakehouse/checkpoints/stream_bronze_silver")
args = ap.parse_args()

spark = SparkSession.builder.appName("lakehouse_stream").getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")
spark.sparkContext.setLogLevel("WARN")
for ns in ("bronze", "silver", "ops"):
    spark.sql(f"CREATE NAMESPACE IF NOT EXISTS {ns}")

# ----------------------------------------------------------------------------------------------- table definitions
# topic suffix -> (silver table or None, primary key, DDL of the Debezium 'after' image, with timestamps as microseconds, dates as days)
SRC = {
    "oltp.product_category_name_translation": ("category_translation", ["product_category_name"], "product_category_name string, product_category_name_english string"),
    "oltp.products": ("products", ["product_id"], "product_id string, product_category_name string, product_name_lenght int, product_description_lenght int, product_photos_qty int, product_weight_g int, product_length_cm int, product_height_cm int, product_width_cm int"),
    "oltp.sellers": ("sellers", ["seller_id"], "seller_id string, seller_zip_code_prefix string, seller_city string, seller_state string"),
    "oltp.customers": ("customers", ["customer_id"], "customer_id string, customer_unique_id string, customer_zip_code_prefix string, customer_city string, customer_state string"),
    "oltp.geolocation": (None, ["id"], "id long, geolocation_zip_code_prefix string, geolocation_lat double, geolocation_lng double, geolocation_city string, geolocation_state string"),
    "oltp.orders": ("orders", ["order_id"], "order_id string, customer_id string, order_status string, order_purchase_timestamp long, order_approved_at long, order_delivered_carrier_date long, order_delivered_customer_date long, order_estimated_delivery_date long"),
    "oltp.order_items": ("order_items", ["order_id", "order_item_id"], "order_id string, order_item_id int, product_id string, seller_id string, shipping_limit_date long, price string, freight_value string"),
    "oltp.order_payments": ("order_payments", ["order_id", "payment_sequential"], "order_id string, payment_sequential int, payment_type string, payment_installments int, payment_value string"),
    "oltp.order_reviews": ("order_reviews", ["review_id", "order_id"], "review_id string, order_id string, review_score int, review_comment_title string, review_comment_message string, review_creation_date long, review_answer_timestamp long"),
    "crm.mql": ("mql", ["mql_id"], "mql_id string, first_contact_date int, landing_page_id string, origin string"),
    "crm.closed_deals": ("closed_deals", ["mql_id"], "mql_id string, seller_id string, sdr_id string, sr_id string, won_date long, business_segment string, lead_type string, lead_behaviour_profile string, has_company boolean, has_gtin boolean, average_stock string, business_type string, declared_product_catalog_size string, declared_monthly_revenue string"),
}
bronze_name = lambda suffix: "bronze." + suffix.replace(".", "_")

SILVER_DDL = {
    "category_translation": "product_category_name string, product_category_name_english string",
    "products": "product_id string, product_category_name string, name_length int, description_length int, photos_qty int, weight_g int, length_cm int, height_cm int, width_cm int, dq_missing_dimensions boolean",
    "sellers": "seller_id string, zip_code_prefix string, city string, state_code string",
    "customers": "customer_id string, customer_unique_id string, zip_code_prefix string, city string, state_code string",
    "orders": "order_id string, customer_id string, order_status string, order_purchase_timestamp timestamp, order_approved_at timestamp, order_delivered_carrier_date timestamp, order_delivered_customer_date timestamp, order_estimated_delivery_date timestamp, dq_flags array<string>, dq_flag_count int",
    "order_items": "order_id string, order_item_id int, product_id string, seller_id string, shipping_limit_date timestamp, price decimal(12,2), freight_value decimal(12,2)",
    "order_payments": "order_id string, payment_sequential int, payment_type string, payment_installments int, payment_value decimal(12,2), dq_flags array<string>",
    "order_reviews": "review_id string, order_id string, review_score smallint, review_comment_title string, review_comment_message string, review_creation_date timestamp, review_answer_timestamp timestamp",
    "mql": "mql_id string, first_contact_date date, landing_page_id string, origin string",
    "closed_deals": "mql_id string, seller_id string, sdr_id string, sr_id string, won_date timestamp, business_segment string, lead_type string, lead_behaviour_profile string, business_type string, has_company string, has_gtin string, average_stock string, declared_product_catalog_size decimal(12,1), declared_monthly_revenue decimal(14,2), dq_flags array<string>",
}
META = "src_ts_ms bigint, processed_at timestamp"          # added to every Silver table


def create_tables():
    for suffix in SRC:
        spark.sql(f"""CREATE TABLE IF NOT EXISTS {bronze_name(suffix)} (key string, payload string, op string, ts_ms bigint, source_table string,
                      kafka_partition int, kafka_offset bigint, kafka_timestamp timestamp, ingested_at timestamp) USING iceberg""")
    for t, ddl in SILVER_DDL.items():
        spark.sql(f"CREATE TABLE IF NOT EXISTS silver.{t} ({ddl}, {META}) USING iceberg")
        if t not in ("category_translation", "products", "sellers", "mql"):
            spark.sql(f"""CREATE TABLE IF NOT EXISTS silver.{t}_rejected (error_code string, reason string, key string, payload string, src_ts_ms bigint,
                          rejected_at timestamp) USING iceberg""")
    spark.sql("""CREATE TABLE IF NOT EXISTS silver.order_status_history (order_id string, status string, valid_from timestamp, valid_to timestamp,
                 is_current boolean, source string, src_ts_ms bigint, processed_at timestamp) USING iceberg""")


S = spark          # replaced by the session of each micro-batch (its DataFrames live in a cloned session)
create_tables()


# ----------------------------------------------------------------------------------------------- cleaning rules (ODS)
def _unaccent(s):
    if s is None:
        return None
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


unaccent_udf = F.udf(_unaccent, T.StringType())
clean_zip = lambda c: F.when(F.regexp_replace(F.coalesce(c, F.lit("")), r"\D", "") == "", F.lit(None)).otherwise(F.substring(F.lpad(F.regexp_replace(c, r"\D", ""), 5, "0"), 1, 5))
clean_city = lambda c: F.when(F.trim(unaccent_udf(F.lower(F.trim(c)))) == "", F.lit(None)).otherwise(F.lower(unaccent_udf(F.trim(c))))
clean_state = lambda c: F.when(F.substring(F.upper(F.trim(c)), 1, 2) == "", F.lit(None)).otherwise(F.substring(F.upper(F.trim(c)), 1, 2))
ts = lambda c: F.timestamp_micros(F.col(c))
unk = lambda c: F.coalesce(F.when(F.trim(c) == "", F.lit(None)).otherwise(F.trim(c)), F.lit("unknown"))


def merge(df, table, keys, view):
    """MERGE the (already de-duplicated) rows into silver.<table>; an older event never replaces a newer row."""
    df.createOrReplaceTempView(view)
    on = " AND ".join(f"t.{k} = s.{k}" for k in keys)
    S.sql(f"""MERGE INTO silver.{table} t USING {view} s ON {on}
                  WHEN MATCHED AND s.src_ts_ms >= t.src_ts_ms THEN UPDATE SET *
                  WHEN NOT MATCHED THEN INSERT *""")


def latest(ev, keys):
    """The newest c/u/r event of every key in the batch (deletes are kept in Bronze; none occur in this data set)."""
    w = Window.partitionBy(*[F.col("after." + k) for k in keys]).orderBy(F.col("ts_ms").desc(), F.col("kafka_offset").desc())
    return ev.filter(F.col("op").isin("c", "u", "r") & F.col("after").isNotNull()).withColumn("_rn", F.row_number().over(w)).filter("_rn = 1").drop("_rn")


def with_meta(df):
    return df.withColumn("processed_at", F.current_timestamp())


def retry_pool(table, ddl, keys, candidates):
    """candidates (struct columns of the Debezium image + ts_ms) UNION the orphans waiting in silver.<table>_rejected; newest per key.
    The result is materialised with localCheckpoint(), NOT persist(): reject_orphans() later deletes the pending orphans from the very table this
    DataFrame reads, and Spark recomputes every cached plan that depends on a table once the table is modified, so a persisted pool silently lost
    the pending orphans (first and second run: half of the orders missing in Silver). A local checkpoint has no lineage to the table."""
    pend = S.table(f"silver.{table}_rejected").filter("error_code = 'orphan'")
    pool = candidates
    n_pend = pend.count()
    print(f"RETRY {table}: pending orphans in silver.{table}_rejected = {n_pend}", flush=True)
    if n_pend:
        parsed = pend.select(F.from_json("payload", ddl).alias("after"), F.col("src_ts_ms").alias("ts_ms"), F.lit(-1).cast("long").alias("kafka_offset"), F.lit("r").alias("op"))
        pool = candidates.unionByName(parsed.select(*candidates.columns))
    pool = latest(pool, keys).localCheckpoint()        # eager: rows are copied out of the table, lineage is cut
    print(f"RETRY {table}: pool after union and de-dup = {pool.count()}", flush=True)
    return pool


def reject_orphans(table, bad, keys, ddl_cols):
    """Replace the pending orphans of the table by the ones still unresolved (resolved ones simply disappear)."""
    had = S.table(f"silver.{table}_rejected").filter("error_code = 'orphan'").limit(1).count()
    if had:
        S.sql(f"DELETE FROM silver.{table}_rejected WHERE error_code = 'orphan'")
    if bad is not None:
        n = bad.count()
        if n:
            bad.select(F.lit("orphan").alias("error_code"), F.col("reason"), F.concat_ws("|", *[F.col("after." + k).cast("string") for k in keys]).alias("key"),
                       F.to_json(F.col("after")).alias("payload"), F.col("ts_ms").alias("src_ts_ms"), F.current_timestamp().alias("rejected_at")).writeTo(f"silver.{table}_rejected").append()


def split_parent(pool, checks):
    """checks = [(after column, parent silver table, parent key column, reason)]. Returns (valid rows, orphan rows with reason)."""
    reason = F.lit(None).cast("string")
    df = pool
    for col, parent, pk, why in checks:
        p = S.table(f"silver.{parent}").select(F.col(pk).alias("_pk_" + parent)).distinct()
        df = df.join(F.broadcast(p), F.col("after." + col) == F.col("_pk_" + parent), "left")
        reason = F.coalesce(reason, F.when(F.col("_pk_" + parent).isNull(), F.lit(why)))
        df = df.withColumn("_reason", reason)
    df = df.drop(*[c for c in df.columns if c.startswith("_pk_")])
    return df.filter("_reason IS NULL").drop("_reason"), df.filter("_reason IS NOT NULL").withColumn("reason", F.col("_reason")).drop("_reason")


# ----------------------------------------------------------------------------------------------- Silver per table
def silver_simple(ev):
    out = {}
    d = latest(ev["oltp.product_category_name_translation"], ["product_category_name"])
    if d.limit(1).count():
        out["category_translation"] = d.count()
        merge(with_meta(d.select(F.trim("after.product_category_name").alias("product_category_name"), F.trim("after.product_category_name_english").alias("product_category_name_english"),
                                 F.col("ts_ms").alias("src_ts_ms"))), "category_translation", ["product_category_name"], "v_cat")
    d = latest(ev["oltp.products"], ["product_id"])
    if d.limit(1).count():
        a = d.select("after.*", F.col("ts_ms").alias("src_ts_ms"))
        out["products"] = a.count()
        merge(with_meta(a.select("product_id", unk(F.col("product_category_name")).alias("product_category_name"), F.col("product_name_lenght").alias("name_length"),
                                 F.col("product_description_lenght").alias("description_length"), "product_photos_qty",
                                 F.col("product_weight_g").alias("weight_g"), F.col("product_length_cm").alias("length_cm"), F.col("product_height_cm").alias("height_cm"),
                                 F.col("product_width_cm").alias("width_cm"),
                                 (F.col("product_weight_g").isNull() | (F.col("product_weight_g") == 0) | F.col("product_length_cm").isNull() | F.col("product_height_cm").isNull() | F.col("product_width_cm").isNull()).alias("dq_missing_dimensions"),
                                 "src_ts_ms").withColumnRenamed("product_photos_qty", "photos_qty")), "products", ["product_id"], "v_prod")
    d = latest(ev["oltp.sellers"], ["seller_id"])
    if d.limit(1).count():
        a = d.select("after.*", F.col("ts_ms").alias("src_ts_ms"))
        out["sellers"] = a.count()
        merge(with_meta(a.select("seller_id", clean_zip(F.col("seller_zip_code_prefix")).alias("zip_code_prefix"), clean_city(F.col("seller_city")).alias("city"),
                                 clean_state(F.col("seller_state")).alias("state_code"), "src_ts_ms")), "sellers", ["seller_id"], "v_sell")
    d = latest(ev["crm.mql"], ["mql_id"])
    if d.limit(1).count():
        a = d.select("after.*", F.col("ts_ms").alias("src_ts_ms"))
        out["mql"] = a.count()
        merge(with_meta(a.select("mql_id", F.date_add(F.lit("1970-01-01").cast("date"), F.col("first_contact_date")).alias("first_contact_date"), "landing_page_id",
                                 unk(F.lower(F.trim(F.col("origin")))).alias("origin"), "src_ts_ms")), "mql", ["mql_id"], "v_mql")
    return out


def silver_customers(ev):
    d = latest(ev["oltp.customers"], ["customer_id"])
    if not d.limit(1).count():
        return {}
    a = d.select("after.*", F.col("ts_ms").alias("src_ts_ms"), F.col("kafka_offset"))
    bad = a.filter(F.trim(F.col("customer_unique_id")).isNull() | (F.trim(F.col("customer_unique_id")) == ""))
    nb = bad.count()
    if nb:
        bad.select(F.lit("missing_customer_unique_id").alias("error_code"), F.lit("missing customer_unique_id").alias("reason"), F.col("customer_id").alias("key"),
                   F.to_json(F.struct("customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state")).alias("payload"),
                   F.col("src_ts_ms"), F.current_timestamp().alias("rejected_at")).writeTo("silver.customers_rejected").append()
    good = a.filter(~(F.trim(F.col("customer_unique_id")).isNull() | (F.trim(F.col("customer_unique_id")) == "")))
    n = good.count()
    merge(with_meta(good.select("customer_id", "customer_unique_id", clean_zip(F.col("customer_zip_code_prefix")).alias("zip_code_prefix"), clean_city(F.col("customer_city")).alias("city"),
                                clean_state(F.col("customer_state")).alias("state_code"), "src_ts_ms")), "customers", ["customer_id"], "v_cust")
    return {"customers": n, "customers_rejected": nb}


def order_flags(c):
    p, a, car, dl, est, st = (F.col(x) for x in ("order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_status"))
    flags = F.array(
        F.when(a < p, F.lit("approved_before_purchase")), F.when(car < p, F.lit("carrier_before_purchase")), F.when(car < a, F.lit("carrier_before_approved")),
        F.when(dl < car, F.lit("delivered_before_carrier")), F.when(dl < p, F.lit("delivered_before_purchase")), F.when(est < p, F.lit("estimated_before_purchase")),
        F.when((st == "delivered") & dl.isNull(), F.lit("delivered_without_date")), F.when((st == "delivered") & car.isNull(), F.lit("delivered_without_carrier_date")),
        F.when((st == "delivered") & a.isNull(), F.lit("delivered_without_approval")), F.when((st != "delivered") & dl.isNotNull(), F.lit("delivery_date_but_not_delivered")))
    return F.filter(flags, lambda x: x.isNotNull())


def status_valid_from():
    """Business time of a status, from the order row: created = purchase, approved, shipped = carrier date, delivered; other statuses at the last known time."""
    return (F.when(F.col("status") == "created", F.col("p")).when(F.col("status") == "approved", F.coalesce(F.col("a"), F.col("p")))
            .when(F.col("status") == "shipped", F.coalesce(F.col("car"), F.col("a"), F.col("p"))).when(F.col("status") == "delivered", F.coalesce(F.col("dl"), F.col("car"), F.col("a"), F.col("p")))
            .otherwise(F.greatest(F.col("p"), F.col("a"), F.col("car"), F.col("dl"))))


def silver_orders(ev):
    allev = ev["oltp.orders"].filter(F.col("op").isin("c", "u", "r") & F.col("after").isNotNull())
    cand = latest(ev["oltp.orders"], ["order_id"]).select("after", "ts_ms", "kafka_offset", "op")
    pool = retry_pool("orders", SRC["oltp.orders"][2], ["order_id"], cand)
    if not pool.limit(1).count() and not allev.limit(1).count():
        return {}
    valid, orphan = split_parent(pool, [("customer_id", "customers", "customer_id", "orphan: customer_id not in silver.customers")])
    reject_orphans("orders", orphan, ["order_id"], None)
    a = valid.select("after.*", F.col("ts_ms").alias("src_ts_ms"))
    a = a.select("order_id", "customer_id", F.lower(F.trim(F.col("order_status"))).alias("order_status"), ts("order_purchase_timestamp").alias("order_purchase_timestamp"),
                 ts("order_approved_at").alias("order_approved_at"), ts("order_delivered_carrier_date").alias("order_delivered_carrier_date"),
                 ts("order_delivered_customer_date").alias("order_delivered_customer_date"), ts("order_estimated_delivery_date").alias("order_estimated_delivery_date"), "src_ts_ms")
    a = a.withColumn("dq_flags", order_flags(None)).withColumn("dq_flag_count", F.size("dq_flags"))
    n = a.count()
    merge(with_meta(a.select("order_id", "customer_id", "order_status", "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date",
                             "order_estimated_delivery_date", "dq_flags", "dq_flag_count", "src_ts_ms")), "orders", ["order_id"], "v_ord")
    hist = status_history(allev, valid)
    return {"orders": n, "orders_orphans": orphan.count(), "order_status_history": hist}


def status_history(allev, valid):
    """One row per status change. CDC events give the changes; snapshot rows (op r) have no earlier history, so the chain is inferred from the timestamps of the row."""
    ids = valid.select(F.col("after.order_id").alias("order_id")).distinct()
    e = allev.join(F.broadcast(ids), allev["after.order_id"] == ids["order_id"], "inner").select(
        F.col("after.order_id").alias("order_id"), F.lower(F.trim(F.col("after.order_status"))).alias("status"), F.timestamp_micros(F.col("after.order_purchase_timestamp")).alias("p"),
        F.timestamp_micros(F.col("after.order_approved_at")).alias("a"), F.timestamp_micros(F.col("after.order_delivered_carrier_date")).alias("car"),
        F.timestamp_micros(F.col("after.order_delivered_customer_date")).alias("dl"), "ts_ms", "kafka_offset", "op")
    e = e.withColumn("vf", status_valid_from())
    cdc = e.filter("op <> 'r'").select("order_id", "status", F.col("vf").alias("valid_from"), F.lit("cdc").alias("source"), "ts_ms", "kafka_offset")
    # snapshot rows: created -> approved -> shipped -> delivered up to the current status; other final statuses appended at the last known time
    snap = e.filter("op = 'r'")
    chain = F.array(F.struct(F.lit("created").alias("status"), F.col("p").alias("vf")), F.struct(F.lit("approved").alias("status"), F.col("a").alias("vf")),
                    F.struct(F.lit("shipped").alias("status"), F.col("car").alias("vf")), F.struct(F.lit("delivered").alias("status"), F.col("dl").alias("vf")))
    keep = F.when(F.col("status") == "created", F.slice(chain, 1, 1)).when(F.col("status") == "approved", F.slice(chain, 1, 2)).when(F.col("status") == "shipped", F.slice(chain, 1, 3)) \
        .when(F.col("status") == "delivered", chain).otherwise(F.slice(chain, 1, 3))
    s = snap.withColumn("c", F.explode(F.filter(keep, lambda x: x["vf"].isNotNull()))).select("order_id", F.col("c.status").alias("status"), F.col("c.vf").alias("valid_from"),
                                                                                             F.lit("snapshot_inferred").alias("source"), "ts_ms", F.lit(-1).cast("long").alias("kafka_offset"))
    other = snap.filter(~F.col("status").isin("created", "approved", "shipped", "delivered")).select("order_id", "status", F.col("vf").alias("valid_from"),
                                                                                                    F.lit("snapshot_inferred").alias("source"), "ts_ms", F.lit(-1).cast("long").alias("kafka_offset"))
    cur = S.table("silver.order_status_history").filter("is_current").join(F.broadcast(ids), "order_id").select(
        "order_id", "status", "valid_from", "source", F.lit(-1).cast("long").alias("ts_ms"), F.lit(-2).cast("long").alias("kafka_offset"))
    allr = cdc.unionByName(s).unionByName(other).unionByName(cur)
    w = Window.partitionBy("order_id").orderBy("valid_from", "ts_ms", "kafka_offset")
    allr = allr.withColumn("prev", F.lag("status").over(w)).filter("prev IS NULL OR prev <> status")       # only real changes
    w2 = Window.partitionBy("order_id").orderBy("valid_from", "ts_ms", "kafka_offset")
    h = allr.withColumn("valid_to", F.lead("valid_from").over(w2)).withColumn("is_current", F.col("valid_to").isNull())
    h = h.select("order_id", "status", "valid_from", "valid_to", "is_current", "source", F.col("ts_ms").alias("src_ts_ms")).withColumn("processed_at", F.current_timestamp())
    h = h.withColumn("src_ts_ms", F.greatest(F.col("src_ts_ms"), F.lit(0).cast("long")))
    h.createOrReplaceTempView("v_hist")
    S.sql("""MERGE INTO silver.order_status_history t USING v_hist s ON t.order_id = s.order_id AND t.status = s.status
                 WHEN MATCHED THEN UPDATE SET t.valid_from = s.valid_from, t.valid_to = s.valid_to, t.is_current = s.is_current, t.processed_at = s.processed_at
                 WHEN NOT MATCHED THEN INSERT *""")
    return h.count()


def child_table(ev, topic, table, keys, ddl_silver, checks, build):
    cand = latest(ev[topic], keys).select("after", "ts_ms", "kafka_offset", "op")
    pool = retry_pool(table, SRC[topic][2], keys, cand)
    if not pool.limit(1).count():
        return {}
    valid, orphan = split_parent(pool, checks)
    reject_orphans(table, orphan, keys, None)
    a = build(valid.select("after.*", F.col("ts_ms").alias("src_ts_ms")))
    n = a.count()
    merge(with_meta(a), table, keys, "v_" + table)
    return {table: n, table + "_orphans": orphan.count()}


def build_items(a):
    return a.select("order_id", "order_item_id", "product_id", "seller_id", ts("shipping_limit_date").alias("shipping_limit_date"), F.col("price").cast("decimal(12,2)").alias("price"),
                    F.col("freight_value").cast("decimal(12,2)").alias("freight_value"), "src_ts_ms")


def build_payments(a):
    flags = F.filter(F.array(F.when(F.coalesce(F.col("payment_installments"), F.lit(0)) == 0, F.lit("installments_zero_set_to_1")),
                             F.when(F.lower(F.trim(F.col("payment_type"))) == "not_defined", F.lit("payment_type_not_defined")),
                             F.when(F.col("payment_value").cast("decimal(12,2)") == 0, F.lit("payment_value_zero"))), lambda x: x.isNotNull())
    return a.select("order_id", "payment_sequential", F.lower(F.trim(F.col("payment_type"))).alias("payment_type"),
                    F.greatest(F.coalesce(F.col("payment_installments"), F.lit(1)), F.lit(1)).alias("payment_installments"), F.col("payment_value").cast("decimal(12,2)").alias("payment_value"),
                    flags.alias("dq_flags"), "src_ts_ms")


def build_reviews(a):
    return a.select("review_id", "order_id", F.col("review_score").cast("smallint").alias("review_score"), "review_comment_title", "review_comment_message",
                    ts("review_creation_date").alias("review_creation_date"), ts("review_answer_timestamp").alias("review_answer_timestamp"), "src_ts_ms")


def build_deals(a):
    flags = F.filter(F.array(F.when(F.col("declared_monthly_revenue").cast("decimal(14,2)") == 0, F.lit("declared_revenue_zero")),
                             F.when(F.col("declared_product_catalog_size").cast("decimal(12,1)") == 0, F.lit("declared_catalog_zero"))), lambda x: x.isNotNull())
    return a.select("mql_id", "seller_id", "sdr_id", "sr_id", ts("won_date").alias("won_date"), unk(F.col("business_segment")).alias("business_segment"), unk(F.col("lead_type")).alias("lead_type"),
                    unk(F.col("lead_behaviour_profile")).alias("lead_behaviour_profile"), unk(F.col("business_type")).alias("business_type"),
                    F.coalesce(F.col("has_company").cast("string"), F.lit("unknown")).alias("has_company"), F.coalesce(F.col("has_gtin").cast("string"), F.lit("unknown")).alias("has_gtin"),
                    unk(F.col("average_stock")).alias("average_stock"), F.col("declared_product_catalog_size").cast("decimal(12,1)").alias("declared_product_catalog_size"),
                    F.col("declared_monthly_revenue").cast("decimal(14,2)").alias("declared_monthly_revenue"), flags.alias("dq_flags"), "src_ts_ms")


# ----------------------------------------------------------------------------------------------- micro-batch
def process_batch(df, epoch_id):
    import time as _t
    global S
    S = df.sparkSession
    S.conf.set("spark.sql.session.timeZone", "UTC")
    t0 = _t.time()
    df.persist()
    n_all = df.count()
    if n_all == 0:
        df.unpersist()
        return
    # ---- Bronze: append every event of every topic, unchanged
    stats = {}
    base = df.select(F.col("key").cast("string").alias("key"), F.col("value").cast("string").alias("payload"), F.get_json_object(F.col("value").cast("string"), "$.op").alias("op"),
                     F.get_json_object(F.col("value").cast("string"), "$.ts_ms").cast("long").alias("ts_ms"), F.col("topic").alias("source_table"),
                     F.col("partition").alias("kafka_partition"), F.col("offset").alias("kafka_offset"), F.col("timestamp").alias("kafka_timestamp"))
    base.persist()
    for suffix in SRC:
        sub = base.filter(F.col("source_table") == "olist." + suffix)
        if sub.limit(1).count():
            sub.withColumn("ingested_at", F.current_timestamp()).writeTo(bronze_name(suffix)).append()
    t_bronze = _t.time()
    # ---- Silver: parse the 'after' image of the batch once per table
    ev = {}
    for suffix, (_s, _k, ddl) in SRC.items():
        ev[suffix] = (base.filter(F.col("source_table") == "olist." + suffix)
                      .withColumn("after", F.from_json(F.get_json_object(F.col("payload"), "$.after"), ddl)))
    stats.update(silver_simple(ev))
    stats.update(silver_customers(ev))
    stats.update(silver_orders(ev))
    stats.update(child_table(ev, "oltp.order_items", "order_items", ["order_id", "order_item_id"], None,
                             [("order_id", "orders", "order_id", "orphan: order_id not in silver.orders"), ("product_id", "products", "product_id", "orphan: product_id not in silver.products"),
                              ("seller_id", "sellers", "seller_id", "orphan: seller_id not in silver.sellers")], build_items))
    stats.update(child_table(ev, "oltp.order_payments", "order_payments", ["order_id", "payment_sequential"], None,
                             [("order_id", "orders", "order_id", "orphan: order_id not in silver.orders")], build_payments))
    stats.update(child_table(ev, "oltp.order_reviews", "order_reviews", ["review_id", "order_id"], None,
                             [("order_id", "orders", "order_id", "orphan: order_id not in silver.orders")], build_reviews))
    stats.update(child_table(ev, "crm.closed_deals", "closed_deals", ["mql_id"], None,
                             [("mql_id", "mql", "mql_id", "orphan: mql_id not in silver.mql")], build_deals))
    base.unpersist()
    df.unpersist()
    t1 = _t.time()
    if args.debug_batches and epoch_id + 1 >= args.debug_batches:
        threading.Thread(target=q.stop, daemon=True).start()
    print(f"BATCH {epoch_id}: {n_all} events, bronze {t_bronze - t0:.1f}s, silver {t1 - t_bronze:.1f}s, {stats}", flush=True)


reader = (spark.readStream.format("kafka").option("kafka.bootstrap.servers", "kafka:9092").option("subscribePattern", r"olist\..*")
          .option("startingOffsets", "earliest").option("maxOffsetsPerTrigger", args.max_offsets).option("failOnDataLoss", "false"))
writer = (reader.load().writeStream.foreachBatch(process_batch).option("checkpointLocation", args.checkpoint))
q = writer.trigger(availableNow=True).start() if args.available_now else writer.trigger(processingTime=f"{args.trigger_seconds} seconds").start()

import threading
import time as _time


def _progress():
    while q.isActive:
        _time.sleep(60)
        lp = q.lastProgress
        if lp:
            print(f"PROGRESS batchId={lp.get('batchId')} numInputRows={lp.get('numInputRows')} inputRowsPerSecond={lp.get('inputRowsPerSecond')} status={q.status.get('message')}", flush=True)


threading.Thread(target=_progress, daemon=True).start()
q.awaitTermination()
print("STREAM_END", flush=True)
