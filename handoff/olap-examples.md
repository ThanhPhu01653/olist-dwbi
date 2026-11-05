# Minh hoạ các thao tác OLAP trên kho (ROLAP) – sinh tự động 2026-11-05 19:51

*Mọi số lấy từ truy vấn thật trên trạng thái cuối của `olist_dw` (đủ dữ liệu). GMV = Σ price của đơn không thuộc nhóm Failed. File SQL nằm ở `sql/60_olap_examples/`; chạy lại bằng `python scripts/run_olap_examples.py`.*

## Vì sao đây là ROLAP, và khác MOLAP ở đâu
- **ROLAP (Relational OLAP)**: dữ liệu nằm trong bảng quan hệ theo lược đồ sao (`dim_*`, `fact_*` trong PostgreSQL); mỗi thao tác OLAP được dịch thành một câu SQL
  (`GROUP BY` / `ROLLUP` / `CUBE` / `GROUPING SETS`, `WHERE` cho slice và dice, `FILTER` cho pivot). Tổng hợp được tính lúc truy vấn (có thể tăng tốc bằng materialized view ở các mart).
- **MOLAP (Multidimensional OLAP)**: dữ liệu được nạp vào một khối đa chiều riêng (ví dụ SQL Server Analysis Services) với các tổng hợp **tính sẵn** và lưu dạng mảng; truy vấn rất nhanh nhưng
  cần bước xử lý (process) khối, tốn thêm dung lượng và khó cập nhật tăng dần khi chiều/measure đổi.
- **Chọn ROLAP** vì dự án dùng PostgreSQL (không có SSAS), dữ liệu chỉ vài trăm nghìn dòng fact nên SQL trả lời dưới 1 giây, kho luôn "tươi" sau mỗi lần nạp tăng dần (không phải process khối),
  và Power BI (chế độ Import + DAX) đóng vai trò lớp ngữ nghĩa cho người dùng cuối. Đổi lại, với dữ liệu hàng trăm triệu dòng thì ROLAP cần thêm tổng hợp tính sẵn hoặc phân vùng.

## Roll-up – `010_rollup.sql`

ROLL-UP: aggregate to a COARSER level of a hierarchy (day -> month -> quarter -> year; zip -> state -> region). ROLLUP(a, b) adds subtotals for (a, b), (a) and the grand total. GROUPING(col) = 1 marks a subtotal row. GROUPING SETS and CUBE give custom / all combinations. Measure: GMV = sum of price of orders not in status group 'Failed'.

### Roll-up thời gian bằng ROLLUP: quý -> năm -> tổng (GMV, 2017-2018)

*10 dòng, 1.03 giây*

| nam | quy | orders | gmv |
| --- | --- | --- | --- |
| 2017 | 2017-Q1 | 5,122 | 733,398.94 |
| 2017 | 2017-Q2 | 9,222 | 1,286,918.78 |
| 2017 | 2017-Q3 | 12,445 | 1,681,949.00 |
| 2017 | 2017-Q4 | 17,586 | 2,406,225.55 |
| 2017 | (cả năm) | 44,375 | 6,108,492.27 |
| 2018 | 2018-Q1 | 20,979 | 2,764,402.78 |
| 2018 | 2018-Q2 | 19,897 | 2,849,730.26 |
| 2018 | 2018-Q3 | 12,655 | 1,727,049.37 |
| 2018 | (cả năm) | 53,531 | 7,341,182.41 |
| Tổng | (cả năm) | 97,906 | 13,449,674.68 |

<details><summary>SQL</summary>

```sql
SELECT CASE WHEN GROUPING(d.year) = 1 THEN 'Tổng' ELSE d.year::text END AS nam,
       CASE WHEN GROUPING(d.year_quarter) = 1 THEN '(cả năm)' ELSE d.year_quarter END AS quy,
       count(DISTINCT f.order_id) AS orders, round(sum(f.price), 2) AS gmv
FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
WHERE d.year IN (2017, 2018)
GROUP BY ROLLUP (d.year, d.year_quarter)
ORDER BY GROUPING(d.year), d.year, GROUPING(d.year_quarter), d.year_quarter;
```

</details>

### Roll-up địa lý bằng ROLLUP: bang -> vùng -> tổng (GMV theo bang của khách; chỉ bang có GMV > 500.000)

*13 dòng, 1.04 giây*

| vung | bang | gmv | orders |
| --- | --- | --- | --- |
| Centro-Oeste | (cả vùng) | 861,825.09 | 5,728 |
| Nordeste | BA | 507,108.83 | 3,344 |
| Nordeste | (cả vùng) | 1,538,314.17 | 9,307 |
| Norte | (cả vùng) | 333,814.28 | 1,834 |
| Sudeste | SP | 5,163,799.21 | 41,126 |
| Sudeste | RJ | 1,811,601.43 | 12,696 |
| Sudeste | MG | 1,573,403.31 | 11,494 |
| Sudeste | (cả vùng) | 8,822,336.08 | 67,334 |
| Sul | RS | 742,469.88 | 5,414 |
| Sul | PR | 676,883.06 | 4,982 |
| Sul | SC | 518,758.18 | 3,600 |
| Sul | (cả vùng) | 1,938,111.12 | 13,996 |
| Tổng | (cả vùng) | 13,494,400.74 | 98,199 |

<details><summary>SQL</summary>

```sql
SELECT CASE WHEN GROUPING(g.region) = 1 THEN 'Tổng' ELSE g.region END AS vung,
       CASE WHEN GROUPING(g.state_code) = 1 THEN '(cả vùng)' ELSE g.state_code END AS bang,
       round(sum(f.price), 2) AS gmv, count(DISTINCT f.order_id) AS orders
FROM dw.fact_order_item f
JOIN dw.dim_geography g ON g.geography_key = f.customer_geography_key
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY ROLLUP (g.region, g.state_code)
HAVING GROUPING(g.region) = 1 OR GROUPING(g.state_code) = 1 OR sum(f.price) > 500000
ORDER BY GROUPING(g.region), g.region, GROUPING(g.state_code), sum(f.price) DESC;
```

</details>

### GROUPING SETS: bốn góc nhìn trong MỘT truy vấn (theo năm, theo vùng, theo nhóm ngành hàng, tổng)

*22 dòng, 0.13 giây*

| nhom | gmv |
| --- | --- |
| Năm 2018 | 7,341,182.41 |
| Năm 2017 | 6,108,492.27 |
| Năm 2016 | 44,726.06 |
| Vùng Sudeste | 8,822,336.08 |
| Vùng Sul | 1,938,111.12 |
| Vùng Nordeste | 1,538,314.17 |
| Vùng Centro-Oeste | 861,825.09 |
| Vùng Norte | 333,814.28 |
| Ngành Home & Furniture | 3,075,408.74 |
| Ngành Gifts & Others | 1,887,892.16 |
| Ngành Electronics & Computers | 1,885,896.23 |
| Ngành Health & Beauty | 1,652,294.44 |
| Ngành Auto, Tools & Construction | 1,549,912.44 |
| Ngành Sports & Leisure | 979,740.92 |
| Ngành Toys & Baby | 891,659.53 |
| Ngành Office & Stationery | 503,174.54 |
| Ngành Fashion & Accessories | 340,870.38 |
| Ngành Books, Media & Music | 268,470.48 |
| Ngành Pet | 213,766.63 |
| Ngành Unknown | 178,572.55 |
| Ngành Food & Drinks | 66,741.70 |
| Tổng | 13,494,400.74 |

<details><summary>SQL</summary>

```sql
SELECT CASE WHEN GROUPING(d.year) = 0 THEN 'Năm ' || d.year WHEN GROUPING(g.region) = 0 THEN 'Vùng ' || g.region
            WHEN GROUPING(p.category_group) = 0 THEN 'Ngành ' || p.category_group ELSE 'Tổng' END AS nhom,
       round(sum(f.price), 2) AS gmv
FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key
JOIN dw.dim_geography g ON g.geography_key = f.customer_geography_key
JOIN dw.dim_product p ON p.product_key = f.product_key
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY GROUPING SETS ((d.year), (g.region), (p.category_group), ())
ORDER BY GROUPING(d.year), GROUPING(g.region), GROUPING(p.category_group), gmv DESC;
```

</details>

### CUBE: mọi tổ hợp tổng con của (năm, vùng) - 4 loại dòng: chi tiết, theo năm, theo vùng, tổng

*18 dòng, 0.10 giây*

| nam | vung | gmv |
| --- | --- | --- |
| 2017 | Sudeste | 3,928,342.74 |
| 2017 | Sul | 883,019.57 |
| 2017 | Nordeste | 727,732.51 |
| 2017 | Centro-Oeste | 401,379.61 |
| 2017 | Norte | 168,017.84 |
| 2017 | Tất cả vùng | 6,108,492.27 |
| 2018 | Sudeste | 4,866,292.63 |
| 2018 | Sul | 1,047,635.66 |
| 2018 | Nordeste | 804,568.34 |
| 2018 | Centro-Oeste | 458,089.53 |
| 2018 | Norte | 164,596.25 |
| 2018 | Tất cả vùng | 7,341,182.41 |
| Tất cả năm | Sudeste | 8,794,635.37 |
| Tất cả năm | Sul | 1,930,655.23 |
| Tất cả năm | Nordeste | 1,532,300.85 |
| Tất cả năm | Centro-Oeste | 859,469.14 |
| Tất cả năm | Norte | 332,614.09 |
| Tất cả năm | Tất cả vùng | 13,449,674.68 |

<details><summary>SQL</summary>

```sql
SELECT coalesce(d.year::text, 'Tất cả năm') AS nam, coalesce(g.region, 'Tất cả vùng') AS vung, round(sum(f.price), 2) AS gmv
FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key AND d.year IN (2017, 2018)
JOIN dw.dim_geography g ON g.geography_key = f.customer_geography_key
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY CUBE (d.year, g.region)
ORDER BY GROUPING(d.year), d.year, GROUPING(g.region), gmv DESC;
```

</details>

## Drill-down – `020_drilldown.sql`

DRILL-DOWN: go from a coarse level to a FINER level of the same hierarchy by adding the next level to GROUP BY and filtering the parent value. Path 1 (time): year -> quarter -> month -> day.  Path 2 (geography): region -> state -> city.

### Drill-down thời gian, bước 1: GMV theo năm

*3 dòng, 0.04 giây*

| year | gmv |
| --- | --- |
| 2,016 | 44,726.06 |
| 2,017 | 6,108,492.27 |
| 2,018 | 7,341,182.41 |

<details><summary>SQL</summary>

```sql
SELECT d.year, round(sum(f.price), 2) AS gmv FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY d.year ORDER BY d.year;
```

</details>

### Drill-down thời gian, bước 2: mở năm 2017 thành các quý

*4 dòng, 0.02 giây*

| year_quarter | gmv |
| --- | --- |
| 2017-Q1 | 733,398.94 |
| 2017-Q2 | 1,286,918.78 |
| 2017-Q3 | 1,681,949.00 |
| 2017-Q4 | 2,406,225.55 |

<details><summary>SQL</summary>

```sql
SELECT d.year_quarter, round(sum(f.price), 2) AS gmv FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key AND d.year = 2017
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY d.year_quarter ORDER BY d.year_quarter;
```

</details>

### Drill-down thời gian, bước 3: mở quý 4/2017 thành các tháng

*3 dòng, 0.01 giây*

| year_month | gmv |
| --- | --- |
| 2017-10 | 660,179.62 |
| 2017-11 | 1,003,862.14 |
| 2017-12 | 742,183.79 |

<details><summary>SQL</summary>

```sql
SELECT d.year_month, round(sum(f.price), 2) AS gmv FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key AND d.year_quarter = '2017-Q4'
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY d.year_month ORDER BY d.year_month;
```

</details>

### Drill-down thời gian, bước 4: mở tháng 11/2017 thành các ngày (10 ngày GMV cao nhất; có Black Friday 24/11)

*10 dòng, 0.01 giây*

| full_date | day_name | is_black_friday | gmv |
| --- | --- | --- | --- |
| 2017-11-24 | Friday | True | 152,653.74 |
| 2017-11-25 | Saturday | False | 60,923.48 |
| 2017-11-27 | Monday | False | 47,923.66 |
| 2017-11-28 | Tuesday | False | 47,886.55 |
| 2017-11-26 | Sunday | False | 44,976.28 |
| 2017-11-20 | Monday | False | 44,235.47 |
| 2017-11-23 | Thursday | False | 43,563.89 |
| 2017-11-29 | Wednesday | False | 39,787.42 |
| 2017-11-21 | Tuesday | False | 34,209.84 |
| 2017-11-30 | Thursday | False | 31,322.74 |

<details><summary>SQL</summary>

```sql
SELECT d.full_date, d.day_name, d.is_black_friday, round(sum(f.price), 2) AS gmv FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key AND d.year_month = '2017-11'
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY d.full_date, d.day_name, d.is_black_friday ORDER BY gmv DESC LIMIT 10;
```

</details>

### Drill-down địa lý: vùng Sudeste -> bang SP -> 5 thành phố có GMV cao nhất

*5 dòng, 0.21 giây*

| state_code | city | gmv | orders |
| --- | --- | --- | --- |
| SP | sao paulo | 1,896,587.25 | 15,287 |
| SP | campinas | 186,865.95 | 1,421 |
| SP | guarulhos | 142,578.38 | 1,167 |
| SP | sao bernardo do campo | 103,930.01 | 921 |
| SP | santos | 98,777.09 | 706 |

<details><summary>SQL</summary>

```sql
SELECT g.state_code, g.city, round(sum(f.price), 2) AS gmv, count(DISTINCT f.order_id) AS orders FROM dw.fact_order_item f
JOIN dw.dim_geography g ON g.geography_key = f.customer_geography_key AND g.region = 'Sudeste' AND g.state_code = 'SP'
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY g.state_code, g.city ORDER BY gmv DESC LIMIT 5;
```

</details>

## Slice – `030_slice.sql`

SLICE: fix ONE dimension to a single value (here year = 2017) and look at the remaining dimensions. The result is a "slice" of the cube with one dimension removed.

### Slice năm 2017: GMV theo tháng

*12 dòng, 0.23 giây*

| year_month | orders | gmv |
| --- | --- | --- |
| 2017-01 | 787 | 120,098.27 |
| 2017-02 | 1,718 | 244,959.35 |
| 2017-03 | 2,617 | 368,341.32 |
| 2017-04 | 2,377 | 353,842.98 |
| 2017-05 | 3,640 | 503,159.19 |
| 2017-06 | 3,205 | 429,916.61 |
| 2017-07 | 3,946 | 492,287.30 |
| 2017-08 | 4,272 | 568,245.79 |
| 2017-09 | 4,227 | 621,415.91 |
| 2017-10 | 4,547 | 660,179.62 |
| 2017-11 | 7,421 | 1,003,862.14 |
| 2017-12 | 5,618 | 742,183.79 |

<details><summary>SQL</summary>

```sql
SELECT d.year_month, count(DISTINCT f.order_id) AS orders, round(sum(f.price), 2) AS gmv FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key AND d.year = 2017
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY d.year_month ORDER BY d.year_month;
```

</details>

### Slice năm 2017: GMV theo vùng (cùng lát cắt, nhìn theo chiều địa lý)

*5 dòng, 0.03 giây*

| region | gmv | pct |
| --- | --- | --- |
| Sudeste | 3,928,342.74 | 64.30 |
| Sul | 883,019.57 | 14.50 |
| Nordeste | 727,732.51 | 11.90 |
| Centro-Oeste | 401,379.61 | 6.60 |
| Norte | 168,017.84 | 2.80 |

<details><summary>SQL</summary>

```sql
SELECT g.region, round(sum(f.price), 2) AS gmv, round(100.0 * sum(f.price) / sum(sum(f.price)) OVER (), 1) AS pct FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key AND d.year = 2017
JOIN dw.dim_geography g ON g.geography_key = f.customer_geography_key
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY g.region ORDER BY gmv DESC;
```

</details>

### Slice năm 2017: GMV theo nhóm ngành hàng

*13 dòng, 0.04 giây*

| category_group | gmv |
| --- | --- |
| Home & Furniture | 1,343,271.64 |
| Gifts & Others | 909,610.50 |
| Electronics & Computers | 900,432.80 |
| Health & Beauty | 695,968.13 |
| Auto, Tools & Construction | 615,372.12 |
| Toys & Baby | 458,921.70 |
| Sports & Leisure | 447,546.59 |
| Office & Stationery | 223,134.83 |
| Fashion & Accessories | 191,747.44 |
| Books, Media & Music | 111,115.44 |
| Unknown | 105,232.67 |
| Pet | 85,023.71 |
| Food & Drinks | 21,114.70 |

<details><summary>SQL</summary>

```sql
SELECT p.category_group, round(sum(f.price), 2) AS gmv FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key AND d.year = 2017
JOIN dw.dim_product p ON p.product_key = f.product_key
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY p.category_group ORDER BY gmv DESC;
```

</details>

## Dice – `040_dice.sql`

DICE: select a SUB-CUBE by restricting SEVERAL dimensions at once (here region = Sudeste x category group = Home & Furniture x quarter 4).

### Dice Sudeste x Home & Furniture x quý 4 (mọi năm có dữ liệu: 2016, 2017; quý 4/2018 chưa có): GMV theo quý và bang

*7 dòng, 0.04 giây*

| year_quarter | state_code | orders | gmv |
| --- | --- | --- | --- |
| 2016-Q4 | SP | 25 | 2,966.41 |
| 2016-Q4 | MG | 10 | 972.44 |
| 2016-Q4 | RJ | 7 | 460.37 |
| 2017-Q4 | SP | 1,787 | 199,178.62 |
| 2017-Q4 | RJ | 627 | 76,525.16 |
| 2017-Q4 | MG | 477 | 54,125.48 |
| 2017-Q4 | ES | 103 | 10,328.72 |

<details><summary>SQL</summary>

```sql
SELECT d.year_quarter, g.state_code, count(DISTINCT f.order_id) AS orders, round(sum(f.price), 2) AS gmv FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key AND d.quarter = 4
JOIN dw.dim_geography g ON g.geography_key = f.customer_geography_key AND g.region = 'Sudeste'
JOIN dw.dim_product p ON p.product_key = f.product_key AND p.category_group = 'Home & Furniture'
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY d.year_quarter, g.state_code ORDER BY d.year_quarter, gmv DESC;
```

</details>

### Dice như trên nhưng chỉ quý 4/2017: 5 danh mục bán chạy nhất trong sub-cube

*5 dòng, 0.04 giây*

| category_name_en | items | gmv |
| --- | --- | --- |
| bed_bath_table | 1,578 | 141,884.85 |
| furniture_decor | 1,089 | 84,685.64 |
| housewares | 720 | 55,102.15 |
| small_appliances | 60 | 13,574.75 |
| home_confort | 65 | 9,111.79 |

<details><summary>SQL</summary>

```sql
SELECT p.category_name_en, count(*) AS items, round(sum(f.price), 2) AS gmv FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key AND d.year_quarter = '2017-Q4'
JOIN dw.dim_geography g ON g.geography_key = f.customer_geography_key AND g.region = 'Sudeste'
JOIN dw.dim_product p ON p.product_key = f.product_key AND p.category_group = 'Home & Furniture'
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY p.category_name_en ORDER BY gmv DESC LIMIT 5;
```

</details>

## Pivot – `050_pivot.sql`

PIVOT: turn the values of one dimension into COLUMNS. PostgreSQL has no PIVOT keyword: use conditional aggregation sum(...) FILTER (WHERE ...) (or the crosstab() function of the tablefunc extension, not installed here).

### Pivot vùng x năm (GMV): mỗi năm là một cột

*5 dòng, 0.07 giây*

| vung | 2016 | 2017 | 2018 | tong |
| --- | --- | --- | --- | --- |
| Sudeste | 27,700.71 | 3,928,342.74 | 4,866,292.63 | 8,822,336.08 |
| Sul | 7,455.89 | 883,019.57 | 1,047,635.66 | 1,938,111.12 |
| Nordeste | 6,013.32 | 727,732.51 | 804,568.34 | 1,538,314.17 |
| Centro-Oeste | 2,355.95 | 401,379.61 | 458,089.53 | 861,825.09 |
| Norte | 1,200.19 | 168,017.84 | 164,596.25 | 333,814.28 |

<details><summary>SQL</summary>

```sql
SELECT g.region AS vung,
       round(coalesce(sum(f.price) FILTER (WHERE d.year = 2016), 0), 2) AS "2016",
       round(coalesce(sum(f.price) FILTER (WHERE d.year = 2017), 0), 2) AS "2017",
       round(coalesce(sum(f.price) FILTER (WHERE d.year = 2018), 0), 2) AS "2018",
       round(sum(f.price), 2) AS tong
FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key
JOIN dw.dim_geography g ON g.geography_key = f.customer_geography_key
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY g.region ORDER BY tong DESC;
```

</details>

### Pivot nhóm ngành hàng x quý của 2017 (tỷ trọng GMV theo hàng, %)

*13 dòng, 0.05 giây*

| nhom_nganh | Q1 | Q2 | Q3 | Q4 | gmv_2017 |
| --- | --- | --- | --- | --- | --- |
| Home & Furniture | 13.10 | 21.90 | 29.80 | 35.20 | 1,343,271.64 |
| Gifts & Others | 10.00 | 21.80 | 26.30 | 41.80 | 909,610.50 |
| Electronics & Computers | 11.10 | 18.10 | 31.80 | 39.00 | 900,432.80 |
| Health & Beauty | 13.60 | 23.90 | 25.40 | 37.20 | 695,968.13 |
| Auto, Tools & Construction | 13.10 | 21.60 | 21.30 | 44.00 | 615,372.12 |
| Toys & Baby | 8.60 | 15.80 | 29.00 | 46.60 | 458,921.70 |
| Sports & Leisure | 11.80 | 20.70 | 28.80 | 38.60 | 447,546.59 |
| Office & Stationery | 15.60 | 17.60 | 24.70 | 42.10 | 223,134.83 |
| Fashion & Accessories | 11.20 | 28.00 | 28.50 | 32.30 | 191,747.44 |
| Books, Media & Music | 7.80 | 24.20 | 29.40 | 38.60 | 111,115.44 |
| Unknown | 16.50 | 23.90 | 13.30 | 46.30 | 105,232.67 |
| Pet | 15.40 | 23.00 | 30.20 | 31.40 | 85,023.71 |
| Food & Drinks | 18.80 | 9.00 | 17.00 | 55.20 | 21,114.70 |

<details><summary>SQL</summary>

```sql
SELECT p.category_group AS nhom_nganh,
       round(100.0 * sum(f.price) FILTER (WHERE d.year_quarter = '2017-Q1') / sum(f.price), 1) AS "Q1",
       round(100.0 * sum(f.price) FILTER (WHERE d.year_quarter = '2017-Q2') / sum(f.price), 1) AS "Q2",
       round(100.0 * sum(f.price) FILTER (WHERE d.year_quarter = '2017-Q3') / sum(f.price), 1) AS "Q3",
       round(100.0 * sum(f.price) FILTER (WHERE d.year_quarter = '2017-Q4') / sum(f.price), 1) AS "Q4",
       round(sum(f.price), 2) AS gmv_2017
FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key AND d.year = 2017
JOIN dw.dim_product p ON p.product_key = f.product_key
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY p.category_group ORDER BY gmv_2017 DESC;
```

</details>

### Pivot hình thức thanh toán x năm (số lần thanh toán)

*5 dòng, 0.14 giây*

| hinh_thuc | 2017 | 2018 | tong |
| --- | --- | --- | --- |
| Credit card | 34,568 | 41,969 | 76,795 |
| Boleto | 9,508 | 10,213 | 19,784 |
| Voucher | 3,027 | 2,725 | 5,775 |
| Debit card | 422 | 1,105 | 1,529 |
| Not defined | 0 | 3 | 3 |

<details><summary>SQL</summary>

```sql
SELECT pt.display_name AS hinh_thuc,
       count(*) FILTER (WHERE d.year = 2017) AS "2017", count(*) FILTER (WHERE d.year = 2018) AS "2018", count(*) AS tong
FROM dw.fact_payment f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key
JOIN dw.dim_payment_type pt ON pt.payment_type_key = f.payment_type_key
GROUP BY pt.display_name ORDER BY tong DESC;
```

</details>
