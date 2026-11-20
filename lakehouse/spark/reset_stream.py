"""Start the streaming pipeline from zero: drop every Bronze (except api_*) and Silver table and delete the streaming checkpoint.
Used after a failed first run or to replay the whole stream.  docker exec lh-spark spark-submit ... reset_stream.py
Never touches bronze.api_* (those come from the landing zone, not from Kafka) or the gold / ops namespaces."""
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("reset_stream").getOrCreate()
for ns, keep in (("bronze", "api_"), ("silver", None)):
    for r in spark.sql(f"SHOW TABLES IN {ns}").collect():
        if keep and r.tableName.startswith(keep):
            continue
        spark.sql(f"DROP TABLE {ns}.{r.tableName} PURGE")
        print("dropped", ns, r.tableName)
jvm = spark._jvm
path = jvm.org.apache.hadoop.fs.Path("s3a://lakehouse/checkpoints/stream_bronze_silver")
fs = path.getFileSystem(spark._jsc.hadoopConfiguration())
print("checkpoint deleted:", fs.delete(path, True))
