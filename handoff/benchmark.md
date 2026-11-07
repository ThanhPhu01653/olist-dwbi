# Benchmark gọn (P7-A) – sinh tự động

Mỗi ô là trung bình 5 lần chạy `EXPLAIN (ANALYZE)` sau 1 lần chạy nóng (cache), đơn vị **mili giây** (execution time, không tính truyền kết quả). Dữ liệu: trạng thái cuối của `olist_dw` (112.650 dòng hàng, 99.441 đơn). Máy dev của Phú (laptop), PostgreSQL mặc định.

## 1. oltp (chuẩn hoá) và dw (star schema)

| Truy vấn | oltp | dw (có index FK) | dw nhanh hơn |
| --- | ---: | ---: | ---: |
| Q1 GMV theo bang × tháng | 657.4 | 506.1 | 1.3× |
| Q2 Lead time theo bang | 85.7 | 53.8 | 1.6× |
| Q3 Scorecard seller | 375.1 | 386.8 | 1.0× |
| Q4 GMV của một seller (tra cứu chọn lọc) | 6.3 | 0.8 | 7.8× |

## 2. dw có và không có index trên khoá ngoại

| Truy vấn | Có index FK | Không index FK | Chậm đi |
| --- | ---: | ---: | ---: |
| Q1 GMV theo bang × tháng | 506.1 | 494.0 | 1.0× |
| Q2 Lead time theo bang | 53.8 | 51.5 | 1.0× |
| Q3 Scorecard seller | 386.8 | 391.3 | 1.0× |
| Q4 GMV của một seller (tra cứu chọn lọc) | 0.8 | 7.3 | 9.0× |

## 3. View thường và materialized view (cùng định nghĩa; Q1, Q2 đọc view mart theo bang × tháng; Q3 là scorecard seller)

| Truy vấn | View thường | Materialized view | Nhanh hơn |
| --- | ---: | ---: | ---: |
| Q1 GMV theo bang × tháng | 770.4 | 0.056 | 13,709× |
| Q2 Lead time theo bang | 165.8 | 0.042 | 3,911× |
| Q3 Scorecard seller | 196.3 | 0.193 | 1,015× |

Chi tiết (min–max, ms): Q1 oltp: 646.0–664.4; Q1 dw: 488.8–539.4; Q1 dw_noidx: 482.5–504.4; Q1 view: 743.0–818.7; Q1 matview: 0.0–0.1; Q2 oltp: 70.1–129.0; Q2 dw: 49.2–63.0; Q2 dw_noidx: 48.4–55.1; Q2 view: 133.3–212.7; Q2 matview: 0.0–0.0; Q3 oltp: 347.3–415.7; Q3 dw: 369.8–403.1; Q3 dw_noidx: 367.5–448.5; Q3 view: 183.8–217.6; Q3 matview: 0.2–0.2; Q4 oltp: 6.0–6.6; Q4 dw: 0.8–0.8; Q4 dw_noidx: 7.2–7.4
