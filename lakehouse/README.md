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
