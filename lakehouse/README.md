# Lakehouse (P10) – chạy từ đầu

Thiết kế và lý do chọn công nghệ: `docs/LAKEHOUSE.md`. README này được hoàn thiện ở Bước 13; hiện có phần hạ tầng.

## Yêu cầu
Docker Desktop (WSL2), `.wslconfig` `memory=4GB` (profile `lite`), PostgreSQL của kho chạy riêng ở cổng 5432 (không dùng ở đây).

## Dựng hạ tầng
PowerShell (từ thư mục gốc dự án):
```powershell
Copy-Item lakehouse\.env.example lakehouse\.env      # rồi điền mật khẩu
cd lakehouse
docker compose --profile lite up -d --build
cd ..
python lakehouse\scripts\check_health.py --wait 150
```
bash / macOS:
```bash
cp lakehouse/.env.example lakehouse/.env
cd lakehouse && docker compose --profile lite up -d --build && cd ..
python lakehouse/scripts/check_health.py --wait 150
```
Dừng: `docker compose --profile lite down` (thêm `-v` để xoá dữ liệu).

## Cổng trên máy (chỉ 127.0.0.1)
| Dịch vụ | Cổng |
| --- | --- |
| PostgreSQL nguồn | 5433 |
| Kafka Connect (REST) | 8083 |
| MinIO (S3 / console) | 9000 / 9001 |
| Iceberg REST catalog | 8181 |
| Trino | 8080 |

## Chạy Spark
Container `lh-spark` chạy không tải; việc được khởi động bằng `docker exec` (Git Bash cần `MSYS_NO_PATHCONV=1`):
```powershell
docker exec lh-spark /opt/spark/bin/spark-sql --master "local[2]" --properties-file /opt/lakehouse/spark/spark-defaults.conf -e "SHOW NAMESPACES"
```

## Luồng Kafka → Bronze → Silver
```powershell
# nạp bù mọi thứ đang có trong Kafka rồi dừng (log ghi vào lakehouse\data\logs\stream.log)
docker exec -d lh-spark sh -c '/opt/spark/bin/spark-submit --master "local[2]" --properties-file /opt/lakehouse/spark/spark-defaults.conf /opt/lakehouse/spark/stream_bronze_silver.py --available-now > /opt/lakehouse/logs/stream.log 2>&1; echo EXIT=$? >> /opt/lakehouse/logs/stream.log'
# chờ có giới hạn (tối đa 10 phút, in tiến độ mỗi 60 giây)
python lakehouse\scripts\wait_log.py lakehouse\data\logs\stream.log --end "^EXIT=" --timeout 580 --every 60
```
Chạy liên tục (micro-batch 30 giây): bỏ `--available-now`. Làm lại từ đầu: `spark/reset_stream.py` (xoá Bronze không phải API, toàn bộ Silver và checkpoint).
Mọi lệnh chờ dùng `wait_log.py` (không bao giờ chờ vô hạn).

## Silver theo lô, Gold (dbt) và đối soát
```powershell
# Silver địa lý (zip), SCD2 địa chỉ khách, Silver của API (chạy sau khi luồng dừng; log ở lakehouse\data\logs)
docker exec -d lh-spark sh -c '/opt/spark/bin/spark-submit --master "local[2]" --py-files /opt/lakehouse/spark/lh_common.py --properties-file /opt/lakehouse/spark/spark-defaults.conf /opt/lakehouse/spark/silver_batch.py > /opt/lakehouse/logs/silver_batch.log 2>&1; echo EXIT=$? >> /opt/lakehouse/logs/silver_batch.log'
# Gold bằng dbt (cần: pip install -r lakehouse\requirements.txt dbt-core dbt-trino)
cd lakehouse; $env:DBT_PROFILES_DIR = "dbt"
dbt seed --project-dir dbt; dbt run --project-dir dbt; dbt test --project-dir dbt
cd ..
# đối soát Gold với olist_dw (kho chương 3)
python lakehouse\scripts\reconcile.py --md handoff\2026-11-19-P10-reconcile.md
```
Phát lại 11 tháng: `python lakehouse\scripts\replay_events.py --speed 30000` (tiến độ lưu trong nguồn, `--restart` để chạy lại từ đầu).
