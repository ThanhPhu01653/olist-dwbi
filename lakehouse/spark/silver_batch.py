"""Silver tables that are rebuilt in batch from Bronze / Silver (idempotent: every run gives the same result).

    docker exec lh-spark /opt/spark/bin/spark-submit --master local[2] --properties-file /opt/lakehouse/spark/spark-defaults.conf \
        /opt/lakehouse/spark/silver_batch.py [geo] [scd2] [api]        (no argument = all three)

geo   silver.geolocation_zip / silver.geolocation_rejected     from bronze.oltp_geolocation, rules of ods.load_geolocation_zip:
      points outside the Brazil bounding box are rejected (not aggregated); one row per zip: median coordinates, most frequent city / state,
      number of points; a zip whose points are all outside keeps its row with NULL coordinates and n_points = 0 (a zip is never lost).
scd2  silver.customer_address_scd2                              SCD type 2 of the customer address by customer_unique_id, the logic of
      dw.load_dim_customer (a new version when the zip changes, ordered by order purchase time), written with MERGE on
      (customer_unique_id, effective_from).
api   silver.ibge_municipio / ibge_population / ibge_gdp / fx_usd_brl / ipca_month / holiday_official / weather_station / weather_daily /
      city_ibge_match (+ silver.api_rejected, ops.api_match_stat)   from bronze.api_*, the parsers of api_ingest/stage.py and the rules of
      sql/30_ods/030_ods_api.sql, with the four city-match tiers of api_ingest/match.py (exact, normalized, fuzzy >= 95 with gap 10, override).
"""
import csv
import json
import math
import re
import sys
from datetime import date, datetime, timedelta

from pyspark.sql import SparkSession, Window, functions as F, types as T

import lh_common as C

spark = SparkSession.builder.appName("silver_batch").getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")
spark.sparkContext.setLogLevel("WARN")
for ns in ("bronze", "silver", "ops"):
    spark.sql(f"CREATE NAMESPACE IF NOT EXISTS {ns}")
what = [a for a in sys.argv[1:] if a in ("geo", "scd2", "api")] or ["geo", "scd2", "api"]
GEO_DDL = "id long, geolocation_zip_code_prefix string, geolocation_lat double, geolocation_lng double, geolocation_city string, geolocation_state string"


def replace_table(df, name):
    df.writeTo(name).using("iceberg").createOrReplace()
    return spark.table(name).count()


# ------------------------------------------------------------------------------------------------------------------ geolocation
def geo():
    b = spark.table("bronze.oltp_geolocation").filter(F.col("op").isin("c", "u", "r"))
    b = b.withColumn("after", F.from_json(F.get_json_object("payload", "$.after"), GEO_DDL))
    w = Window.partitionBy("after.id").orderBy(F.col("ts_ms").desc(), F.col("kafka_offset").desc())
    g = b.withColumn("_rn", F.row_number().over(w)).filter("_rn = 1").select("after.*", "ts_ms")
    g = g.select("id", C.clean_zip(F.col("geolocation_zip_code_prefix")).alias("zip"), F.col("geolocation_lat").alias("lat"), F.col("geolocation_lng").alias("lng"),
                 C.clean_city(F.col("geolocation_city")).alias("city"), C.clean_state(F.col("geolocation_state")).alias("st"), "ts_ms")
    inside = F.col("lat").between(-33.75, 5.27) & F.col("lng").between(-73.99, -34.79)          # NULL when a coordinate is missing (neither rejected nor used)
    rej = g.filter(inside == F.lit(False))
    n_rej = replace_table(rej.select(F.lit("outside_brazil_bbox").alias("error_code"), F.lit("coordinates outside Brazil bounding box").alias("reason"),
                                     F.col("id").cast("string").alias("key"), F.to_json(F.struct("id", "zip", "lat", "lng", "city", "st")).alias("payload"),
                                     F.col("ts_ms").alias("src_ts_ms"), F.current_timestamp().alias("rejected_at")), "silver.geolocation_rejected")

    def mode_of(df, col):
        c = df.filter(F.col(col).isNotNull()).groupBy("zip", col).count()
        w = Window.partitionBy("zip").orderBy(F.col("count").desc(), F.col(col).asc())
        return c.withColumn("_r", F.row_number().over(w)).filter("_r = 1").select("zip", F.col(col).alias(col))

    valid = g.filter(inside)
    agg = valid.groupBy("zip").agg(F.expr("percentile(lat, 0.5)").alias("latitude"), F.expr("percentile(lng, 0.5)").alias("longitude"), F.count(F.lit(1)).cast("int").alias("n_points"))
    z1 = agg.join(mode_of(valid, "city"), "zip", "left").join(mode_of(valid, "st"), "zip", "left")
    allz = g.filter(F.col("zip").isNotNull()).select("zip").distinct().join(agg.select("zip").withColumn("_has", F.lit(1)), "zip", "left").filter("_has IS NULL").select("zip")
    z2 = (allz.join(mode_of(g, "city"), "zip", "left").join(mode_of(g, "st"), "zip", "left")
          .withColumn("latitude", F.lit(None).cast("double")).withColumn("longitude", F.lit(None).cast("double")).withColumn("n_points", F.lit(0)))
    out = z1.unionByName(z2.select(*z1.columns)).select(F.col("zip").alias("zip_code_prefix"), "latitude", "longitude", F.col("city"), F.col("st").alias("state_code"),
                                                        "n_points", F.current_timestamp().alias("processed_at"))
    n = replace_table(out, "silver.geolocation_zip")
    print(f"SILVER_BATCH geo: geolocation_zip {n} rows, geolocation_rejected {n_rej} rows", flush=True)


# ------------------------------------------------------------------------------------------------------------------ SCD2
def scd2():
    c = spark.table("silver.customers").select("customer_id", "customer_unique_id", "zip_code_prefix", "city", "state_code")
    o = spark.table("silver.orders").select("customer_id", "order_id", "order_purchase_timestamp")
    ev = c.join(o, "customer_id", "left").select(F.col("customer_unique_id").alias("uid"), F.col("zip_code_prefix").alias("zip"), "city", F.col("state_code").alias("st"),
                                                 F.col("order_purchase_timestamp").alias("ts"), "order_id")
    w = Window.partitionBy("uid").orderBy(F.col("ts").asc_nulls_first(), F.col("order_id").asc())
    ordd = ev.withColumn("pz", F.lag("zip").over(w)).withColumn("rn", F.row_number().over(w))
    opening = ordd.filter((F.col("rn") == 1) | ~F.col("zip").eqNullSafe(F.col("pz")))
    w2 = Window.partitionBy("uid", F.coalesce(F.to_date("ts"), F.lit("1900-01-01").cast("date"))).orderBy(F.col("rn").desc())
    stt = opening.withColumn("dup", F.row_number().over(w2)).filter("dup = 1").select("uid", "zip", "city", "st", F.to_date("ts").alias("d"), "rn")
    w3 = Window.partitionBy("uid").orderBy("rn")
    ver = stt.withColumn("vn", F.row_number().over(w3)).withColumn("nxt", F.lead("d").over(w3))
    ver = ver.select(F.col("uid").alias("customer_unique_id"), F.col("zip").alias("zip_code_prefix"), "city", F.col("st").alias("state_code"),
                     F.when(F.col("vn") == 1, F.lit("1900-01-01").cast("date")).otherwise(F.col("d")).alias("effective_from"),
                     F.coalesce(F.date_sub(F.col("nxt"), 1), F.lit("9999-12-31").cast("date")).alias("effective_to"), F.col("nxt").isNull().alias("is_current"),
                     F.col("vn").cast("int").alias("version_no"), F.current_timestamp().alias("processed_at"))
    spark.sql("""CREATE TABLE IF NOT EXISTS silver.customer_address_scd2 (customer_unique_id string, zip_code_prefix string, city string, state_code string,
                 effective_from date, effective_to date, is_current boolean, version_no int, processed_at timestamp) USING iceberg""")
    ver.createOrReplaceTempView("v_scd2")
    spark.sql("""MERGE INTO silver.customer_address_scd2 t USING v_scd2 s ON t.customer_unique_id = s.customer_unique_id AND t.effective_from = s.effective_from
                 WHEN MATCHED AND (t.effective_to <> s.effective_to OR t.is_current <> s.is_current OR t.version_no <> s.version_no OR NOT (t.zip_code_prefix <=> s.zip_code_prefix))
                      THEN UPDATE SET *
                 WHEN NOT MATCHED THEN INSERT *""")
    r = spark.sql("SELECT count(*) n, count(DISTINCT customer_unique_id) c, sum(CASE WHEN is_current THEN 1 ELSE 0 END) cur FROM silver.customer_address_scd2").first()
    print(f"SILVER_BATCH scd2: {r.n} versions, {r.c} customers, {r.cur} current", flush=True)


# ------------------------------------------------------------------------------------------------------------------ API
def files(src):
    """{file_name: payload} of the latest run date of every file of bronze.api_<src> (like api_ingest.stage.latest_file)."""
    rows = spark.table(f"bronze.api_{src}").filter("file_name <> 'manifest.json'").select("run_date", "file_name", "payload").collect()
    best = {}
    for r in rows:
        if r.file_name not in best or r.run_date > best[r.file_name][0]:
            best[r.file_name] = (r.run_date, r.payload)
    return {k: v[1] for k, v in best.items()}


def all_runs(src, prefix):
    """Every run of the files starting with prefix, oldest first (Banco Central series are appended run after run)."""
    rows = spark.table(f"bronze.api_{src}").filter(F.col("file_name").startswith(prefix)).select("run_date", "file_name", "payload").orderBy("run_date", "file_name").collect()
    return rows


def parse_municipios(body):
    rows = []
    for m in body:
        mic = m.get("microrregiao") or {}
        mes = mic.get("mesorregiao") or {}
        imm = m.get("regiao-imediata") or {}
        inter = imm.get("regiao-intermediaria") or {}
        uf = (mes.get("UF") or inter.get("UF") or {})
        rows.append((m["id"], m["nome"], uf.get("id"), uf.get("sigla"), mic.get("nome"), mes.get("nome")))
    return rows


def parse_sidra(body):
    out = []
    for var in body:
        for res in var["resultados"]:
            for s in res["series"]:
                code = int(s["localidade"]["id"])
                for period, value in s["serie"].items():
                    out.append((code, int(period), value))
    return out


def api():
    rej = []          # (source_table, reason, record json)
    f = files("ibge")
    mun = parse_municipios(json.loads(f["municipios.json"]))
    mun = [r for r in mun if r[3] is not None]
    mdf = spark.createDataFrame(mun, "ibge_code int, name string, state_ibge_code int, state_code string, microrregiao string, mesorregiao string")
    mdf = mdf.withColumn("name_key", C.name_key(F.col("name"))).select("ibge_code", "name", "name_key", "state_code", "state_ibge_code", "microrregiao", "mesorregiao")
    n_mun = replace_table(mdf.withColumn("processed_at", F.current_timestamp()), "silver.ibge_municipio")

    def sidra(name, table, col, cast):
        rows = parse_sidra(json.loads(f[name + ".json"]))
        ok = [(c, y, v) for c, y, v in rows if v is not None and re.fullmatch(r"[0-9]+", v)]
        for c, y, v in rows:
            if v is None or not re.fullmatch(r"[0-9]+", v):
                rej.append((f"api.ibge_{name}", f"value not available in the API ({v})", json.dumps({"ibge_code": c, "year": y, "value": v})))
        df = spark.createDataFrame(ok, "ibge_code int, year int, value string").select("ibge_code", "year", F.col("value").cast(cast).alias(col))
        return replace_table(df.withColumn("processed_at", F.current_timestamp()), table)

    n_pop = sidra("populacao", "silver.ibge_population", "population", "bigint")
    n_gdp = sidra("pib", "silver.ibge_gdp", "gdp_thousand_brl", "decimal(18,0)")

    # Banco Central: USD/BRL forward filled over every calendar day 2016-01-01 .. 2020-12-31, IPCA chained index (first month = 100)
    series = {1: {}, 433: {}}
    for r in all_runs("bcb", "sgs_"):
        code = int(r.file_name.split("_")[1])
        for x in json.loads(r.payload):
            series[code][datetime.strptime(x["data"], "%d/%m/%Y").date()] = x["valor"]
    fx_ok = {d: v for d, v in series[1].items() if v is not None and re.fullmatch(r"[0-9.]+", v)}
    for d, v in series[1].items():
        if d not in fx_ok:
            rej.append(("api.bcb_serie", "rate is not a number", json.dumps({"ref_date": str(d), "value": v})))
    days = sorted(fx_ok)
    out, i, last = [], 0, None
    d = date(2016, 1, 1)
    while d <= date(2020, 12, 31):
        while i < len(days) and days[i] <= d:
            last = days[i]
            i += 1
        if last is not None:
            out.append((d, float(fx_ok[last]), last, last == d))
        d += timedelta(days=1)
    fx = spark.createDataFrame(out, "rate_date date, usd_brl double, rate_source_date date, is_business_day boolean").withColumn("usd_brl", F.col("usd_brl").cast("decimal(10,4)"))
    n_fx = replace_table(fx.withColumn("processed_at", F.current_timestamp()), "silver.fx_usd_brl")
    ip_ok = sorted((d, v) for d, v in series[433].items() if v is not None and re.fullmatch(r"-?[0-9.]+", v))
    for d, v in series[433].items():
        if v is None or not re.fullmatch(r"-?[0-9.]+", v):
            rej.append(("api.bcb_serie", "change is not a number", json.dumps({"ref_date": str(d), "value": v})))
    rows, acc = [], 0.0
    for k, (d, v) in enumerate(ip_ok):
        if k > 0:
            acc += math.log(1 + float(v) / 100)
        rows.append((d, float(v), round(100 * math.exp(acc), 6)))
    ip = spark.createDataFrame(rows, "month_date date, change_pct double, ipca_index double").select("month_date", F.col("change_pct").cast("decimal(8,4)").alias("change_pct"),
                                                                                                       F.col("ipca_index").cast("decimal(14,6)").alias("ipca_index"))
    n_ip = replace_table(ip.withColumn("processed_at", F.current_timestamp()), "silver.ipca_month")

    # BrasilAPI holidays
    hol = []
    for name, payload in sorted(files("holidays").items()):
        if name.startswith("feriados_"):
            hol += [(h["date"], h["name"].strip(), h.get("type")) for h in json.loads(payload)]
    hol = sorted(set(hol), key=lambda x: (x[0], x[1]))
    hdf = spark.createDataFrame(hol, "holiday_date string, name string, type string").select(F.to_date("holiday_date").alias("holiday_date"), "name", "type")
    n_hol = replace_table(hdf.withColumn("processed_at", F.current_timestamp()), "silver.holiday_official")

    # Open-Meteo: one station (state capital) per state, daily precipitation
    st_rows, wd = [], []
    wf = files("weather")
    for name, payload in sorted(wf.items()):
        if not name.startswith("geocode_"):
            continue
        uf = name[len("geocode_"):-len(".json")]
        arch = wf.get(f"archive_{uf}.json")
        if arch is None:
            continue
        geo_ = json.loads(payload)
        hit = next(r for r in geo_["results"] if r.get("country_code") == "BR" and r.get("feature_code") in ("PPLA", "PPLC"))
        st_rows.append((uf, hit["name"], hit["latitude"], hit["longitude"]))
        dly = json.loads(arch)["daily"]
        for t, v in zip(dly["time"], dly["precipitation_sum"]):
            if v is None:
                rej.append(("api.weather_daily", "no precipitation value that day", json.dumps({"state_code": uf, "obs_date": t})))
            else:
                wd.append((uf, t, float(v)))
    n_st = replace_table(spark.createDataFrame(st_rows, "state_code string, city string, latitude double, longitude double").withColumn("processed_at", F.current_timestamp()), "silver.weather_station")
    wdf = spark.createDataFrame(wd, "state_code string, obs_date string, precip_mm double").select("state_code", F.to_date("obs_date").alias("obs_date"), F.col("precip_mm").cast("decimal(7,2)").alias("precip_mm"))
    n_wd = replace_table(wdf.withColumn("processed_at", F.current_timestamp()), "silver.weather_daily")

    # city match: (state, city) pairs built like dw.load_dim_geography, then four tiers
    cust, sell = spark.table("silver.customers"), spark.table("silver.sellers")
    other = cust.select(F.col("zip_code_prefix").alias("zip"), "city", F.col("state_code").alias("st")).unionByName(sell.select(F.col("zip_code_prefix").alias("zip"), "city", F.col("state_code").alias("st"))).filter("zip IS NOT NULL")

    def mode_col(df, col):
        c = df.filter(F.col(col).isNotNull()).groupBy("zip", col).count()
        w = Window.partitionBy("zip").orderBy(F.col("count").desc(), F.col(col).asc())
        return c.withColumn("_r", F.row_number().over(w)).filter("_r = 1").select("zip", F.col(col).alias("o_" + col))

    oth = other.select("zip").distinct().join(mode_col(other, "city"), "zip", "left").join(mode_col(other, "st"), "zip", "left")
    gz = spark.table("silver.geolocation_zip").select(F.col("zip_code_prefix").alias("gzip"), F.col("city").alias("gcity"), F.col("state_code").alias("gst"))
    z = gz.join(oth, gz["gzip"] == oth["zip"], "full").select(F.coalesce("gzip", "zip").alias("zip"), F.coalesce("gcity", "o_city").alias("city"), F.coalesce("gst", "o_st").alias("st"))
    pairs = z.filter("city IS NOT NULL AND st IS NOT NULL").groupBy("st", "city").agg(F.count(F.lit(1)).cast("int").alias("zips")).collect()
    mun_rows = spark.table("silver.ibge_municipio").select("state_code", "name", "name_key", "ibge_code").collect()
    by_exact = {(m.state_code, m.name.lower()): m.ibge_code for m in mun_rows}
    keyc = {}
    for m in mun_rows:
        keyc.setdefault((m.state_code, m.name_key), []).append(m.ibge_code)
    by_key = {k: v[0] for k, v in keyc.items() if len(v) == 1}
    by_state = {}
    for m in mun_rows:
        by_state.setdefault(m.state_code, []).append((m.name_key, m.ibge_code))
    valid = {m.ibge_code: m.state_code for m in mun_rows}
    overrides = {}
    with open("/opt/lakehouse/seeds/city_ibge_override.csv", encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if valid.get(int(r["ibge_code"])) != r["state_code"]:
                raise ValueError(f"override {r['city']} -> {r['ibge_code']} is not a municipality of {r['state_code']}")
            overrides[(r["state_code"], r["city"])] = int(r["ibge_code"])
    matched, unmatched = [], []
    for p in pairs:
        st, city = p.st, p.city
        if (st, city) in by_exact:
            matched.append((st, city, by_exact[(st, city)], "exact", 100.0))
            continue
        nk = C.py_name_key(city)
        if nk is not None and (st, nk) in by_key:
            matched.append((st, city, by_key[(st, nk)], "normalized", 100.0))
            continue
        hit = C.fuzzy_pick(city, by_state.get(st, []))
        if hit:
            matched.append((st, city, hit[0], "fuzzy", hit[1]))
        elif (st, city) in overrides:
            matched.append((st, city, overrides[(st, city)], "override", 100.0))
        else:
            unmatched.append((st, city, p.zips))
            rej.append(("silver.city_ibge_match", "city not matched to an IBGE municipality (no exact, normalized, fuzzy or override match; often a district or neighbourhood)",
                        json.dumps({"state_code": st, "city": city, "zips": p.zips})))
    mt = spark.createDataFrame(matched, "state_code string, city string, ibge_code int, method string, score double").select("state_code", "city", "ibge_code", "method", F.col("score").cast("decimal(5,1)").alias("score"))
    n_match = replace_table(mt.withColumn("processed_at", F.current_timestamp()), "silver.city_ibge_match")
    zips = {(p.st, p.city): p.zips for p in pairs}
    stat = {}
    for st, city, code, method, _ in matched:
        s = stat.setdefault(method, [0, 0]); s[0] += 1; s[1] += zips[(st, city)]
    s = stat.setdefault("unmatched", [0, 0])
    for st, city, zz in unmatched:
        s[0] += 1; s[1] += zz
    replace_table(spark.createDataFrame([(k, v[0], v[1]) for k, v in sorted(stat.items())], "method string, city_pairs int, zips long").withColumn("computed_at", F.current_timestamp()), "ops.api_match_stat")
    replace_table(spark.createDataFrame(rej or [("-", "-", "{}")], "source_table string, reason string, record string").filter("source_table <> '-'").withColumn("rejected_at", F.current_timestamp()), "silver.api_rejected")
    print(f"SILVER_BATCH api: municipio {n_mun}, population {n_pop}, gdp {n_gdp}, fx {n_fx}, ipca {n_ip}, holidays {n_hol}, stations {n_st}, weather {n_wd}, "
          f"match {n_match} pairs, unmatched {len(unmatched)}, rejected {len(rej)}; tiers {json.dumps({k: v for k, v in stat.items()})}", flush=True)


for step in what:
    {"geo": geo, "scd2": scd2, "api": api}[step]()
