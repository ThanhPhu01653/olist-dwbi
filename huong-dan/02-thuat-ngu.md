# 02 – Thuật ngữ Kho dữ liệu & BI (kèm ví dụ ngay trong dự án)

*Mỗi thuật ngữ: định nghĩa 1–2 câu + ví dụ chỉ thẳng vào bảng/cột của dự án (số liệu từ `olist_dw`, trạng thái cuối). Tra cột cụ thể ở `03-tu-dien-du-lieu.md`.*

## A. Mô hình chiều
| Thuật ngữ | Định nghĩa | Ví dụ trong dự án |
| --- | --- | --- |
| **Data warehouse (kho dữ liệu)** | Cơ sở dữ liệu tích hợp, lưu lịch sử, tổ chức theo chủ đề để phân tích (khác OLTP phục vụ giao dịch hằng ngày). | Schema `dw` của `olist_dw`: 10 bảng chiều + 6 bảng fact, 614.223 dòng, gộp hai nguồn (bán hàng `oltp`, marketing `crm`). |
| **OLTP** | Hệ thống xử lý giao dịch: chuẩn hoá cao, tối ưu ghi nhanh từng bản ghi. | `oltp.orders`, `oltp.order_items`… (9 bảng) mô phỏng hệ thống bán hàng; `crm.mql`, `crm.closed_deals` là hệ thống marketing. |
| **Fact (bảng sự kiện)** | Bảng chứa các **con số đo** (measure) của một quy trình nghiệp vụ, mỗi dòng là một sự kiện, kèm khoá sang các chiều. | `fact_order_item`: `price`, `freight_value`, `item_total` của từng dòng hàng (112.650 dòng). |
| **Dimension (bảng chiều)** | Bảng mô tả "ai / cái gì / ở đâu / khi nào" để lọc, nhóm các số đo. | `dim_product` (danh mục, nhóm ngành hàng, cỡ hàng), `dim_date`, `dim_geography`. |
| **Measure (độ đo)** | Con số cộng/tính được trên fact. *Additive* cộng được theo mọi chiều; *semi-additive* cộng theo vài chiều; *non-additive* không cộng (dùng trung bình, tỷ lệ). | `price` additive; `declared_monthly_revenue` (fact_lead_funnel) non-additive: dùng AVG/median. Trong Power BI, measure là công thức DAX như `GMV`. |
| **Grain (độ mịn)** | Câu trả lời cho "một dòng của bảng fact là gì?". Chọn grain đầu tiên khi thiết kế. | `fact_order_item`: 1 sản phẩm trong 1 đơn; `fact_order_fulfillment`: 1 đơn; `fact_seller_monthly`: 1 seller × 1 tháng. |
| **Star schema (lược đồ sao)** | Một fact ở giữa nối trực tiếp với các chiều (không chuẩn hoá thêm chiều). | `fact_order_item` nối `dim_date`, `dim_customer`, `dim_geography`, `dim_seller`, `dim_product`, `dim_order_status`. |
| **Constellation (chòm sao)** | Nhiều fact dùng chung các chiều. | 6 fact chia sẻ `dim_date`, `dim_seller`, `dim_customer`… (xem `figures/3-3-4_constellation.png`). |
| **Bus matrix** | Ma trận fact × chiều để lên kế hoạch chiều dùng chung. | `docs/DW_DESIGN.md` mục 4. |
| **Surrogate key (khoá thay thế)** | Khoá số nguyên tự tăng do kho sinh ra, thay cho khoá nghiệp vụ; không mang ý nghĩa. | `seller_key = 2997` thay cho `seller_id = 1900267e…`; `date_key = 20171024` là ngoại lệ có ý nghĩa (yyyymmdd). Dòng Unknown luôn `-1`. |
| **Natural (business) key** | Khoá của hệ thống nguồn. | `seller_id`, `product_id`, `customer_unique_id`, `zip_code_prefix`. |
| **Degenerate dimension** | Mã giao dịch nằm thẳng trong fact, không có bảng chiều riêng. | `order_id`, `order_item_id` trong `fact_order_item`; `mql_id` trong `fact_lead_funnel`. |
| **Conformed dimension (chiều dùng chung)** | Một chiều có cùng ý nghĩa với nhiều fact/quy trình, nhờ đó so sánh xuyên quy trình. | `dim_seller` nối quy trình bán hàng (`fact_order_item`) với thu hút seller (`fact_lead_funnel`); `dim_date`. |
| **Junk dimension** | Gom nhiều cờ/thuộc tính nhỏ, ít giá trị khác nhau vào một chiều thay vì rải vào fact. | `dim_lead_profile`: tổ hợp 7 thuộc tính của deal → 503 dòng (gồm dòng −1). |
| **Role-playing dimension** | Một bảng chiều đóng nhiều vai trong cùng fact. | `dim_date` là ngày mua / duyệt / bàn giao / giao / dự kiến của `fact_order_fulfillment`; `dim_geography` là địa lý khách và địa lý seller; `dim_sales_rep` là SDR và SR. Trong Power BI: quan hệ Inactive + `USERELATIONSHIP`. |
| **Unknown member (dòng −1)** | Dòng đặc biệt để fact không bao giờ có khoá rỗng. | `dim_seller` có `seller_key = -1`; mốc chưa xảy ra (đơn chưa giao) có `delivered_date_key = -1`. |
| **Hierarchy (phân cấp)** | Chuỗi cấp từ chi tiết đến tổng hợp trong một chiều, dùng cho roll-up/drill-down. | Ngày → Tháng → Quý → Năm; Zip → Thành phố → Bang → Vùng; Sản phẩm → Danh mục → Nhóm ngành hàng. |

## B. Thay đổi theo thời gian (SCD) và các loại fact
| Thuật ngữ | Định nghĩa | Ví dụ trong dự án |
| --- | --- | --- |
| **SCD loại 1** | Ghi đè giá trị cũ, không giữ lịch sử. | `dim_seller`: nếu seller đổi thành phố, dòng cũ bị cập nhật. |
| **SCD loại 2** | Giữ lịch sử bằng cách thêm dòng mới cho mỗi thay đổi, có `effective_from/to`, `is_current`. | `dim_customer`: 96.096 khách → 96.339 dòng; 236 khách đổi mã bưu chính (cao nhất 4 phiên bản). Đơn cũ vẫn trỏ về địa chỉ lúc mua. |
| **Transaction fact** | Mỗi dòng là một sự kiện đã xảy ra, thêm mới, không sửa. | `fact_order_item`, `fact_payment`, `fact_review`. |
| **Periodic snapshot fact** | Chụp trạng thái định kỳ (mỗi kỳ một dòng cho mỗi đối tượng). | `fact_seller_monthly`: 36.583 dòng seller × tháng, **dày đặc** (có cả tháng không bán, `orders = 0`). |
| **Accumulating snapshot fact** | Một dòng cho cả vòng đời của một quy trình, được **cập nhật** khi đi qua mốc mới. | `fact_order_fulfillment` (5 mốc ngày: mua → duyệt → bàn giao → giao, ngày dự kiến); `fact_lead_funnel` (liên hệ → chốt → đơn đầu). Mốc chưa xảy ra = `-1`. |
| **Factless / lag** | Các khoảng thời gian giữa mốc, tính sẵn trong fact. | `lead_days`, `handling_days`, `transit_days`, `delay_days`, `promised_days`. |

## C. Dòng dữ liệu (ETL)
| Thuật ngữ | Định nghĩa | Ví dụ trong dự án |
| --- | --- | --- |
| **ETL / ELT** | Extract (lấy) – Transform (biến đổi) – Load (nạp). Dự án: Python điều phối, biến đổi chính bằng SQL procedure. | `python -m etl.run_pipeline`. |
| **Staging** | Vùng đệm chứa bản sao thô của nguồn. | `staging.stg_orders`… thêm `load_batch_id`, `loaded_at`. |
| **ODS (Operational Data Store)** | Lớp dữ liệu đã làm sạch, chuẩn hoá, chưa chuyển thành mô hình chiều. | `ods.orders` có `dq_flags`; `ods.customers` có zip `char(5)`. |
| **Data quality flag (`dq_flags`)** | Cờ đánh dấu lỗi mà **không xoá** dòng. | `carrier_before_approved` (1.359 đơn), `carrier_before_purchase` (166). |
| **Rejected rows** | Dòng không nạp được, ghi cùng lý do. | `etl_log.rejected_rows`: 42 điểm toạ độ ngoài Brazil. |
| **Full load** | Xoá và nạp lại toàn bộ. | `run_pipeline --mode full` (khoảng 56 giây trên dữ liệu đến 2017-12-31). |
| **Incremental load (nạp tăng dần)** | Chỉ nạp dữ liệu mới/thay đổi từ lần trước. | 11 đợt hằng tháng 01–11/2018, mỗi đợt ~20 giây gồm cả test. |
| **Watermark (dấu mốc)** | Giá trị đánh dấu "đã nạp đến đâu", lần sau chỉ lấy phần lớn hơn. | `etl_log.watermark`: mốc `order_purchase_timestamp` của đơn đã vào staging. |
| **Upsert** | Chèn nếu chưa có, cập nhật nếu đã có. | `fact_order_fulfillment` cập nhật theo `order_id` khi đơn đi qua mốc mới. |
| **Idempotent** | Chạy lại nhiều lần cho cùng kết quả, không sinh trùng. | Chạy lại `run_pipeline --mode incremental` → 0 dòng chèn, 0 cập nhật. |
| **Orphan (dòng mồ côi)** | Dòng con mà dòng cha chưa tồn tại. | Deal của MQL `b91cf88…` nếu đến trước MQL; được thử lại ở đợt sau (cơ chế `ods.take_orphans`). |
| **Batch / lô** | Một lần chạy ETL, có `batch_id`. | `etl_log.job_run`, `v_run_summary`. |
| **Data lineage / mapping** | Ánh xạ cột nguồn → đích và phép biến đổi. | `docs/mapping.csv`, `docs/mapping_oltp_olap.md`. |

## D. Phân tích và OLAP
| Thuật ngữ | Định nghĩa | Ví dụ trong dự án |
| --- | --- | --- |
| **Data mart** | Tập con của kho theo chủ đề, tổng hợp sẵn cho một nhóm người dùng. | `mart_sales`, `mart_fulfillment`, `mart_cx`, `mart_acquisition` (17 view). |
| **View / Materialized view** | View: câu truy vấn lưu tên, tính lại mỗi lần đọc. Materialized view: **lưu sẵn kết quả**, phải làm mới. | `mart_cx.v_customer_rfm` (materialized, 94.983 dòng, đọc < 1 ms) so với view thường 150–750 ms; làm mới bằng `dw.refresh_marts`. |
| **OLAP** | Phân tích đa chiều tương tác: roll-up, drill-down, slice, dice, pivot. | `handoff/olap-examples.md` (17 truy vấn). |
| **ROLAP** | OLAP trên CSDL quan hệ: thao tác dịch thành SQL, tổng hợp tính lúc truy vấn. | Dự án dùng ROLAP (SQL `ROLLUP`, `CUBE`, `FILTER`) + Power BI. |
| **MOLAP** | OLAP trên khối đa chiều tính sẵn (ví dụ SSAS): rất nhanh nhưng phải xử lý lại khi dữ liệu đổi. | Không dùng vì PostgreSQL không có SSAS; dữ liệu nhỏ. |
| **Roll-up / Drill-down** | Đi lên cấp tổng hợp hơn / xuống cấp chi tiết hơn của phân cấp. | Quý → Năm; Năm → Quý → Tháng → Ngày (`020_drilldown.sql`). |
| **Slice / Dice** | Slice: cố định một chiều. Dice: giới hạn nhiều chiều (sub-cube). | Slice năm 2017; dice Sudeste × Home & Furniture × quý 4. |
| **Pivot** | Xoay giá trị của một chiều thành cột. | GMV theo vùng × năm bằng `sum(...) FILTER (WHERE d.year = 2017)`. |
| **KPI** | Chỉ số đo hiệu quả. | GMV 13,49 triệu BRL; On-time rate 93,2%; Avg review 4,09. |
| **GMV** | Gross Merchandise Value: tổng giá hàng bán ra. Ở đây: Σ `price` của đơn không thuộc nhóm Failed (13.494.400,74). | `Σ price` mọi đơn là 13.591.643,70 – **khác GMV**. |
| **Pareto 80/20** | Một phần nhỏ nguyên nhân tạo phần lớn kết quả. | 18/74 danh mục tạo 80% GMV (`v_category_pareto`). |
| **RFM** | Phân khúc khách theo Recency (gần đây), Frequency (tần suất), Monetary (giá trị). | `mart_cx.v_customer_rfm`: 6 phân khúc. |
| **Cohort** | Nhóm khách theo tháng mua đầu, xem tỷ lệ quay lại theo thời gian. | `mart_cx.v_customer_cohort`. |
| **Funnel (phễu)** | Chuỗi bước giảm dần. | MQL → chốt deal → có đơn: 8.000 → 842 → 380. |
| **Time intelligence** | Hàm DAX so sánh theo thời gian (MoM, YoY, YTD). | `GMV MoM %`, `GMV YoY %` (`powerbi/measures.md`). |

## E. Power BI
| Thuật ngữ | Định nghĩa | Ví dụ trong dự án |
| --- | --- | --- |
| **Semantic model (mô hình ngữ nghĩa)** | Tập bảng + quan hệ + measure mà các visual dùng. | 16 bảng dim/fact, 32 quan hệ (`powerbi/model.md`). |
| **DAX** | Ngôn ngữ công thức của Power BI. | `GMV = CALCULATE(SUM(fact_order_item[price]), KEEPFILTERS(dim_order_status[status_group] <> "Failed"))`. |
| **Power Query / M** | Công cụ nạp và biến đổi dữ liệu trước khi vào mô hình. | Hàm `fnCsv` và tham số `DataFolder`. |
| **Import mode** | Dữ liệu được nạp vào file `.pbix` (ảnh chụp), cần cho Publish to web. | CSV trong `exports/powerbi/`. |
| **Slicer** | Bộ lọc người dùng bấm trực tiếp trên trang. | `dim_date[year]`, `dim_geography[region]`. |
| **Conditional formatting** | Tô màu theo điều kiện/giá trị. | `Color On-time rate` (< 90% đỏ, < 95% vàng, còn lại xanh). |
| **Row-level filter / bộ lọc trang** | Bộ lọc cố định cho một trang/báo cáo. | `dim_date[InWindow] = TRUE` (2017-01 → 2018-08). |
| **Publish to web** | Xuất báo cáo thành link công khai. | Xem `powerbi/model.md` mục 9. |
