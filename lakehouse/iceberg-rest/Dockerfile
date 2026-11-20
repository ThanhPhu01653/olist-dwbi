# Iceberg REST catalog with a durable PostgreSQL backend.
# The upstream image (apache/iceberg-rest-fixture:1.10.0) only ships the SQLite JDBC driver, so the catalog would live in a file
# inside the container. Same jar, plus the PostgreSQL driver, started with an explicit classpath (java -jar ignores -cp).
FROM apache/iceberg-rest-fixture:1.10.0
ADD --chmod=644 https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.4/postgresql-42.7.4.jar /opt/postgresql.jar
CMD ["java", "-cp", "/usr/lib/iceberg-rest/iceberg-rest-adapter.jar:/opt/postgresql.jar", "org.apache.iceberg.rest.RESTCatalogServer"]
