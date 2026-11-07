# Dựng mô hình và dashboard Power BI – hướng dẫn từng bước

Hướng dẫn từng bước dựng mô hình và dashboard; làm tuần tự từ mục 1 (không cần truy cập database). Cả nhóm dùng **một file `.pbix` chung** (dựng xong gửi nhau qua Drive); các dashboard chia nhau làm (phân công làm sau).
Tài liệu đi kèm: `powerbi/measures.md` (code DAX và giá trị kỳ vọng để đối chiếu), `powerbi/theme.json` (màu và font), `exports/powerbi/README.md` (danh sách file CSV và cột).

## 1. Chuẩn bị
1. Cài **Power BI Desktop** (miễn phí, chỉ có cho Windows). Dùng bản mới nhất.
2. Lấy thư mục CSV **`powerbi`** (link Google Drive ở `exports/README.md`), giải nén/lưu vào một chỗ cố định trên máy, ví dụ `C:\Olist\powerbi`. Trong đó có file `fact_order_item.csv`, `dim_date.csv`, … Đừng đổi tên file.
3. Mở Power BI Desktop → **File → New**. Lưu ngay thành `Olist_DW_BI.pbix`.
4. Nạp theme: tab **View → Themes → Browse for themes** → chọn `powerbi/theme.json` (trong repo). Màu xanh dương = dữ liệu chính, cam = so sánh, xanh lá = tốt, vàng = chú ý, đỏ = xấu; font Segoe UI.

## 2. Tạo tham số `DataFolder` và hàm `fnCsv`
Mục đích: **mọi truy vấn đọc CSV qua một tham số duy nhất**. Đổi máy hoặc thay thư mục CSV mới chỉ cần đổi giá trị tham số (hoặc bấm Refresh nếu đường dẫn không đổi).

**2.1 Tạo tham số**
1. Tab **Home → Transform data** (mở cửa sổ *Power Query Editor*).
2. Tab **Home → Manage Parameters → New Parameter**.
3. Điền: *Name* = `DataFolder`; *Type* = **Text**; *Suggested Values* = **Any value**; *Current Value* = đường dẫn thư mục CSV trên **máy của bạn, không có dấu `\` ở cuối**, ví dụ `C:\Olist\powerbi`. → **OK**.

**2.2 Tạo hàm `fnCsv`** (đọc một file CSV và đặt kiểu cột)
1. Trong Power Query Editor: **Home → New Source → Blank Query**.
2. **Home → Advanced Editor**, xoá hết, dán đoạn sau, bấm **Done**:
```m
(fileName as text, types as list) as table =>
let
    Source   = Csv.Document(File.Contents(DataFolder & "\" & fileName), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed    = Table.TransformColumnTypes(Promoted, types, "en-US")
in
    Typed
```
3. Đổi tên truy vấn thành `fnCsv` (chuột phải ở danh sách bên trái → *Rename*). Đây là một **hàm** (biểu tượng *fx*), không phải bảng; bỏ chọn *Enable load* nếu có hỏi.
Giải thích: `Encoding = 65001` là UTF-8; `"en-US"` để dấu thập phân `.` được hiểu đúng (không bị lẫn với dấu phẩy kiểu Việt/Brazil).

## 3. Nạp các bảng
### 3.1 Bảng nào cần nạp
| Nhóm | Bảng (tên = tên file CSV) | Dùng cho |
| --- | --- | --- |
| Chiều (10) | `dim_date`, `dim_geography`, `dim_customer`, `dim_seller`, `dim_product`, `dim_order_status`, `dim_payment_type`, `dim_lead_origin`, `dim_lead_profile`, `dim_sales_rep` | mọi dashboard |
| Fact (6) | `fact_order_item`, `fact_order_fulfillment`, `fact_payment`, `fact_review`, `fact_lead_funnel`, `fact_seller_monthly` | mọi dashboard |
| Mart (15, *bảng rời, không tạo quan hệ*) | `v_sales_daily`, `v_sales_category_month`, `v_sales_state_month`, `v_category_pareto`, `v_fulfillment_state_month`, `v_status_funnel`, `v_review_vs_delay`, `v_payment_mix_month`, `v_customer_rfm`, `v_customer_cohort`, `v_funnel_by_origin_month`, `v_seller_scorecard`, `v_seller_by_channel`, `v_geo_state`, `v_geo_zip` | các visual đặc biệt (Pareto, cohort, RFM, funnel, scorecard, bản đồ) – mục 8 |
| Giám sát ETL (6, *bảng rời*) | `job_run`, `v_run_summary`, `v_dq_summary`, `v_rejected_summary`, `batch_metrics`, `fact_load_issue` | chỉ D7 |

### 3.2 Cách nạp một bảng
1. Trong Power Query Editor: **Home → New Source → Blank Query** → **Advanced Editor**.
2. Dán đúng 1 đoạn `let Source = fnCsv("<tên file>.csv", { ... }) in Source` của bảng đó trong **Phụ lục** (cuối tài liệu) → **Done**. Danh sách `{{"cột", kiểu}, ...}` đã khai báo kiểu dữ liệu của **từng cột** (xem bảng quy đổi dưới).
3. Đổi tên truy vấn đúng bằng tên bảng (ví dụ `fact_order_item`). Nếu Power BI báo *Formula.Firewall* hoặc hỏi quyền truy cập file, chọn *Ignore privacy levels* / *Continue* (dữ liệu cục bộ).
4. Lặp lại cho các bảng khác. Xong thì **Close & Apply** (tab *Home* của Power Query). Lần đầu mất khoảng 1–3 phút (khoảng 70 MB).

Quy đổi kiểu (đã dùng trong Phụ lục): số nguyên → `Int64.Type` (Whole number); số có phần thập phân → `type number` (Decimal number); chữ → `type text`; ngày → `type date`; ngày giờ → `type datetime`; đúng/sai → `type logical` (True/False).
Gợi ý: cột tiền (`price`, `freight_value`, `payment_value`, `gmv`…) có thể đổi *Format* thành *Fixed decimal / Currency* trong Model view nếu thích; không bắt buộc.

### 3.3 Xử lý riêng `dim_date` (quan trọng)
Bảng ngày phải **không có dòng trống** mới đánh dấu được là *Date table*, nên:
1. Mở truy vấn `dim_date` → **Home → Advanced Editor** và viết lại thành (bước `Base` chính là dòng `Source = fnCsv(...)` trong Phụ lục):
```m
let
    Base    = fnCsv("dim_date.csv", { ...giữ nguyên danh sách cột trong Phụ lục... }),
    NoUnk   = Table.SelectRows(Base, each [date_key] <> -1),
    Window  = Table.AddColumn(NoUnk, "InWindow", each [year_month] >= "2017-01" and [year_month] <= "2018-08", type logical)
in
    Window
```
2. `InWindow` = TRUE cho các ngày thuộc **2017-01 → 2018-08** (giai đoạn dữ liệu đáng tin: 2016 chỉ vài trăm đơn, 09–10/2018 gần như trống). Dùng làm bộ lọc trang ở mục 8.
3. Việc bỏ dòng Unknown (-1) khiến các mốc chưa xảy ra (ví dụ đơn chưa giao) trỏ vào dòng *(Blank)* của bảng ngày: bình thường, không phải lỗi.

## 4. Quan hệ (Model view)
Mở **Model view** (biểu tượng thứ 3 bên trái). Kéo cột khoá từ **fact** thả lên cột khoá của **dim** (hoặc **Manage relationships → New**). Tất cả quan hệ: **Many-to-one (*:1)**, **Cross-filter direction = Single** (lọc từ dim xuống fact). Quan hệ *Inactive* thì bỏ chọn **Make this relationship active**.
Power BI có thể tự dò quan hệ theo tên cột: **xoá các quan hệ tự động** rồi tạo đúng bảng dưới đây.

| # | Từ (nhiều) – bảng[cột] | Đến (một) – bảng[cột] | Cardinality | Trạng thái |
| ---: | --- | --- | --- | --- |
| 1 | fact_order_item[purchase_date_key] | dim_date[date_key] | *:1 | **Active** |
| 2 | fact_order_item[shipping_limit_date_key] | dim_date[date_key] | *:1 | Inactive |
| 3 | fact_order_item[customer_key] | dim_customer[customer_key] | *:1 | Active |
| 4 | fact_order_item[customer_geography_key] | dim_geography[geography_key] | *:1 | **Active** (địa lý khách) |
| 5 | fact_order_item[seller_geography_key] | dim_geography[geography_key] | *:1 | Inactive (địa lý seller) |
| 6 | fact_order_item[seller_key] | dim_seller[seller_key] | *:1 | Active |
| 7 | fact_order_item[product_key] | dim_product[product_key] | *:1 | Active |
| 8 | fact_order_item[order_status_key] | dim_order_status[order_status_key] | *:1 | Active |
| 9 | fact_order_fulfillment[purchase_date_key] | dim_date[date_key] | *:1 | **Active** |
| 10 | fact_order_fulfillment[approved_date_key] | dim_date[date_key] | *:1 | Inactive |
| 11 | fact_order_fulfillment[carrier_date_key] | dim_date[date_key] | *:1 | Inactive |
| 12 | fact_order_fulfillment[delivered_date_key] | dim_date[date_key] | *:1 | Inactive |
| 13 | fact_order_fulfillment[estimated_date_key] | dim_date[date_key] | *:1 | Inactive |
| 14 | fact_order_fulfillment[customer_key] | dim_customer[customer_key] | *:1 | Active |
| 15 | fact_order_fulfillment[customer_geography_key] | dim_geography[geography_key] | *:1 | Active |
| 16 | fact_order_fulfillment[order_status_key] | dim_order_status[order_status_key] | *:1 | Active |
| 17 | fact_payment[purchase_date_key] | dim_date[date_key] | *:1 | Active |
| 18 | fact_payment[customer_key] | dim_customer[customer_key] | *:1 | Active |
| 19 | fact_payment[payment_type_key] | dim_payment_type[payment_type_key] | *:1 | Active |
| 20 | fact_review[review_creation_date_key] | dim_date[date_key] | *:1 | **Active** |
| 21 | fact_review[review_answer_date_key] | dim_date[date_key] | *:1 | Inactive |
| 22 | fact_review[customer_key] | dim_customer[customer_key] | *:1 | Active |
| 23 | fact_lead_funnel[first_contact_date_key] | dim_date[date_key] | *:1 | **Active** |
| 24 | fact_lead_funnel[won_date_key] | dim_date[date_key] | *:1 | Inactive |
| 25 | fact_lead_funnel[first_sale_date_key] | dim_date[date_key] | *:1 | Inactive |
| 26 | fact_lead_funnel[lead_origin_key] | dim_lead_origin[lead_origin_key] | *:1 | Active |
| 27 | fact_lead_funnel[lead_profile_key] | dim_lead_profile[lead_profile_key] | *:1 | Active |
| 28 | fact_lead_funnel[seller_key] | dim_seller[seller_key] | *:1 | Active |
| 29 | fact_lead_funnel[sdr_key] | dim_sales_rep[sales_rep_key] | *:1 | Active (SDR) |
| 30 | fact_lead_funnel[sr_key] | dim_sales_rep[sales_rep_key] | *:1 | Inactive (SR) |
| 31 | fact_seller_monthly[month_date_key] | dim_date[date_key] | *:1 | Active |
| 32 | fact_seller_monthly[seller_key] | dim_seller[seller_key] | *:1 | Active |

Không tạo: `dim_customer[geography_key]` và `dim_seller[geography_key]` → `dim_geography` (sẽ tạo đường lọc thứ hai, gây mơ hồ); `fact_review[order_id]` → `fact_order_fulfillment` (cũng gây mơ hồ – dùng hai cột `delivered_late` và `is_delivered` có sẵn trong `fact_review`); các bảng mart và bảng giám sát ETL để rời.
Khi Power BI cảnh báo "ambiguous path" nghĩa là đã lỡ tạo thừa quan hệ: xoá hoặc chuyển thành Inactive.

**Role-playing date với `USERELATIONSHIP`**: mỗi fact chỉ **một** quan hệ ngày Active (in đậm ở bảng); các quan hệ ngày Inactive được "bật" tạm trong từng measure bằng
`CALCULATE ( [measure], USERELATIONSHIP ( fact[cột_ngày], dim_date[date_key] ) )` – xem các measure *by shipping limit date*, *by delivery date*, *by won date* trong `measures.md` (mục 8). Tương tự, `GMV by seller state` bật quan hệ #5 để xem GMV theo địa lý seller. Hai vai trò SDR/SR của `dim_sales_rep`: #29 Active (SDR), #30 Inactive (SR).

## 5. Thiết lập bảng sau khi nạp
1. **Đánh dấu bảng ngày**: chọn `dim_date` → *Table tools* → **Mark as date table** → cột `full_date`.
2. **Sắp xếp theo cột** (chọn cột → *Column tools → Sort by column*): `dim_date[month_name]` theo `month`; `dim_date[day_name]` theo `day_of_week`; `v_review_vs_delay[delay_bucket]` theo `delay_bucket_no`; `v_status_funnel[stage]` theo `stage_no`.
3. **Data category** (cho bản đồ): `dim_geography[latitude]` = Latitude, `[longitude]` = Longitude, `[state_code]` = State or Province, `[city]` = City, `[country]` = Country/Region.
4. **Cột tính toán** trên `fact_order_fulfillment` (chuột phải bảng → *New column*, dán từng dòng):
```dax
Delay bucket =
SWITCH (
    TRUE (),
    fact_order_fulfillment[is_delivered] = 0, "Chưa giao",
    fact_order_fulfillment[delay_days] < 0, "Giao sớm",
    fact_order_fulfillment[delay_days] = 0, "Đúng ngày dự kiến",
    fact_order_fulfillment[delay_days] <= 3, "Trễ 1-3 ngày",
    fact_order_fulfillment[delay_days] <= 7, "Trễ 4-7 ngày",
    "Trễ trên 7 ngày"
)
```
```dax
Delay bucket order =
SWITCH (
    TRUE (),
    fact_order_fulfillment[is_delivered] = 0, 0,
    fact_order_fulfillment[delay_days] < 0, 1,
    fact_order_fulfillment[delay_days] = 0, 2,
    fact_order_fulfillment[delay_days] <= 3, 3,
    fact_order_fulfillment[delay_days] <= 7, 4,
    5
)
```
→ rồi đặt `Delay bucket` *Sort by column* = `Delay bucket order`.
5. **Ẩn khỏi Report view** (chuột phải → *Hide in report view*) mọi cột `*_key`, `etl_batch_id`, và các bảng mart / ETL không muốn thấy trong danh sách trường. Giữ `date_key` ẩn nhưng dùng `full_date` làm trục thời gian.
6. **Tạo measure**: làm theo `powerbi/measures.md` (mục "Cách dùng"), rồi đối chiếu giá trị kỳ vọng ở cuối file đó.

## 6. Phân cấp (Hierarchies)
Cách tạo: trong khung **Data**, chuột phải cột cấp cao nhất → **Add to hierarchy → New hierarchy**, rồi kéo các cột cấp thấp hơn thả vào hierarchy; đổi tên theo bảng.

| Bảng | Tên phân cấp | Các cấp (từ cao xuống thấp) |
| --- | --- | --- |
| dim_date | Date | `year` → `year_quarter` → `year_month` → `full_date` |
| dim_date | Week | `year` → `week_of_year` → `full_date` |
| dim_geography | Geography | `region` → `state_code` → `city` → `zip_code_prefix` |
| dim_product | Product | `category_group` → `category_name_en` → `product_id` |
| dim_seller | Seller location | `state_code` → `city` → `seller_id` |
| dim_seller | Acquisition | `acquisition_channel` → `acquisition_origin` → `seller_id` |
| dim_customer | Customer location | `state_code` → `city` → `customer_unique_id` |
| dim_lead_origin | Lead origin | `channel_group` → `origin` |
| dim_order_status | Status | `status_group` → `order_status` |
| dim_payment_type | Payment | `payment_group` → `display_name` |

Dùng phân cấp trên visual để **drill-down** (mũi tên xuống) và **roll-up** (mũi tên lên) – đây chính là thao tác OLAP ở phía Power BI (xem `handoff/olap-examples.md` cho phía SQL).

## 7. Bộ lọc thời gian và quy ước chung
- **Dashboard D1–D6**: ở khung *Filters on this page* kéo `dim_date[InWindow]` vào, chọn **TRUE** (2017-01 → 2018-08). Với các bảng mart (đã có cột `in_window`) kéo `in_window` = TRUE. Nếu muốn chỉ định khoảng khác, dùng slicer `dim_date[year_month]` dạng *Between*.
- **D7** (giám sát ETL) **không lọc thời gian**.
- Ghi **cỡ mẫu** trên mọi visual so sánh nhóm nhỏ (đặc biệt D6): đặt thêm `Active sellers`/`MQLs` cạnh tỷ lệ, dùng measure `Small sample warning`.
- Dòng *Unknown* của các chiều hiện là `unknown` / `n/a` / `Unknown`: giữ để thấy dữ liệu thiếu, hoặc lọc bỏ có chủ đích.
- Mọi số tiền là BRL. GMV không gồm đơn Failed – ghi chú này ở chân trang D1.

## 8. Gợi ý từng dashboard
Cỡ trang 16:9; mỗi trang có tiêu đề, dòng chú thích nguồn ("Nguồn: kho dữ liệu Olist, GMV không gồm đơn hủy") và bộ lọc thời gian. Measure viết **đậm** là trong `measures.md`.

### D1 – Executive Overview
| Thành phần | Gợi ý |
| --- | --- |
| Thẻ KPI (card) | **GMV**, **Orders**, **AOV**, **On-time rate**, **Avg review**, **Cancel rate** (tô màu bằng measure `Color …`) |
| Đường (line) | trục `dim_date[year_month]`, giá trị **GMV**; thêm đường **GMV last year** làm đối chiếu |
| Cột | **GMV MoM %** theo tháng (màu theo **Color growth**) |
| Cột ngang | **GMV** theo `dim_geography[region]` |
| Thanh ngang top 10 | **GMV** theo `dim_product[category_group]` |
| Slicer | `dim_date[year]`, `dim_geography[region]`, `dim_order_status[status_group]` |

### D2 – Sales & Product
| Thành phần | Gợi ý |
| --- | --- |
| Treemap | `dim_product[category_group]` → **GMV** |
| Ma trận (matrix) | hàng = phân cấp **Product**, cột = `dim_date[year_quarter]`, giá trị **GMV**, **Items**, **AOV** (drill-down được) |
| Pareto | combo "cột + đường" từ `v_category_pareto`: trục `category_name_en` (sắp theo `gmv_rank`), cột `gmv`, đường `cum_share_pct`; tô màu theo `abc_class` |
| Scatter | trục x **AOV**, trục y **Freight ratio**, chi tiết `category_group` |
| Slicer | `dim_date[year_quarter]`, `dim_product[category_group]`, `dim_product[size_class]`, `dim_geography[state_code]` |

### D3 – Order Fulfillment
| Thành phần | Gợi ý |
| --- | --- |
| Thẻ KPI | **On-time rate**, **Avg lead days**, **Avg promised days**, **Promised vs actual (days)** (màu theo **Color promised vs actual**), **Cancel rate** |
| Funnel | `v_status_funnel`: `stage` (sắp theo `stage_no`) → `orders` (lọc `in_window`) |
| Cột chồng | theo `year_month`: **Avg approval hours** (đổi sang ngày nếu cần), **Avg handling days**, **Avg transit days** |
| Bản đồ / thanh | **Late rate** theo `dim_geography[state_code]` (tô màu theo **Color On-time rate**) |
| Cột nhóm | **Avg promised days** so với **Avg lead days** theo `dim_geography[region]` (ngày hứa so với ngày giao thực tế) |
| Cột | số đơn theo `fact_order_fulfillment[Delay bucket]` |
| Slicer | `dim_date[year_month]`, `dim_geography[region]`, `dim_order_status[order_status]` |

### D4 – Geography & Freight
| Thành phần | Gợi ý |
| --- | --- |
| Bản đồ bong bóng | vị trí = `dim_geography[latitude]`/`[longitude]` (hoặc bảng rời `v_geo_state` theo bang, `v_geo_zip` theo zip: đã có sẵn toạ độ, số đơn, GMV), kích thước **GMV**, màu **Freight ratio** (zip chưa có toạ độ sẽ không hiện) |
| Ma trận | phân cấp **Geography**, giá trị **GMV**, **Freight**, **Freight ratio**, **Avg lead days** |
| Cột | **Freight ratio** theo `state_code` (màu theo **Color Freight ratio**) |
| So sánh vai trò | **GMV** (địa lý khách) cạnh **GMV by seller state** (địa lý seller) theo `region` |
| Slicer | `dim_date[year]`, `dim_product[category_group]`, `dim_product[size_class]` |

### D5 – Customer Experience
| Thành phần | Gợi ý |
| --- | --- |
| Thẻ KPI | **Avg review** (màu theo **Color Avg review**), **% negative**, **Repeat customer rate**, **Avg installments** |
| Cột | `v_review_vs_delay`: trục `delay_bucket` (sắp theo `delay_bucket_no`), giá trị `avg_score` (review không nối được với `Delay bucket` của fulfillment nên dùng bảng mart này) |
| Cột phân bố | `fact_review[review_score]` → **Reviews** |
| Donut | cơ cấu thanh toán: `dim_payment_type[display_name]` → **Payment value** (**Payment share**) |
| Cột | `v_customer_rfm[segment]` → số khách (đếm `customer_unique_id`) |
| Ma trận nhiệt (cohort) | `v_customer_cohort`: hàng `cohort_month`, cột `months_since`, giá trị `retention_pct` (Conditional formatting → *Color scale*) |
| Slicer | `dim_date[year_month]`, `dim_geography[region]` |

### D6 – Seller Acquisition & Performance (2 trang)
**Trang 1 – Funnel theo kênh**
| Thành phần | Gợi ý |
| --- | --- |
| Funnel | **MQLs** → **Won deals** → **Sellers with first sale** |
| Thanh | **MQL to won rate** theo `dim_lead_origin[origin]` (kèm **MQLs** để thấy cỡ mẫu) |
| Cột | **Avg days to close** theo `dim_lead_origin[channel_group]` |
| Đường | **MQLs** theo `year_month` (tháng liên hệ đầu), tách theo `channel_group` |
| Thẻ | **Won to first sale rate**, **Avg days won to first sale**, **Seller GMV first 90d** |
| Slicer | `dim_lead_origin[channel_group]`, `dim_lead_profile[business_segment]` |

**Trang 2 – Seller từ funnel và hiệu suất** (luôn có **Small sample warning**)
| Thành phần | Gợi ý |
| --- | --- |
| Bảng | `v_seller_scorecard` lọc `is_from_funnel = TRUE`: `seller_id`, `acquisition_channel`, `orders`, `gmv`, `late_rate_pct`, `avg_review_score`, `small_sample` |
| Cột + cảnh báo | `v_seller_by_channel`: `acquisition_channel` → `gmv_per_selling_seller`, kèm `selling_sellers` và `small_sample` |
| Scatter | `v_seller_scorecard`: x `gmv`, y `late_rate_pct`, kích thước `orders` (seller GMV cao nhưng hay trễ) |
| Thẻ | Số deal chốt nhưng chưa có đơn = **Won deals** − **Sellers with first sale** (ghi rõ đây là một kết quả, không phải lỗi) |
| Slicer | `v_seller_scorecard[acquisition_channel]`, `[state_code]` |
Lưu ý: trang 2 dùng bảng mart (không chịu bộ lọc ngày); nhớ ghi "toàn bộ giai đoạn" trên tiêu đề.

### D7 – Data Quality & ETL Monitor (không lọc thời gian)
| Thành phần | Gợi ý |
| --- | --- |
| Bảng | `v_run_summary`: `batch_id`, `mode`, `started_at`, `duration_sec`, `status`, `staging_rows`, `ods_inserted`, `ods_rejected`, `dw_inserted`, `dw_updated` (lọc `mode` = full/incremental) |
| Cột | `duration_sec` theo `batch_id` của các lô `incremental` |
| Đường | `batch_metrics`: `mql`, `deals_won`, `sellers_with_sale` theo `batch_id` (funnel lấp đầy dần) và `gmv` |
| Thẻ | tỷ lệ test đạt = `pass_pct` của lô mới nhất (`v_dq_summary`); số dòng bị loại (`v_rejected_summary`) |
| Thanh | `v_rejected_summary`: `reason` → `row_count` |
| Bảng | `fact_load_issue` (khoá rơi về Unknown, khoảng thời gian âm) |
| Slicer | `v_run_summary[mode]` |
Các bảng này nối với nhau bằng `batch_id` nhưng **đừng tạo quan hệ**; mỗi visual dùng một bảng.

## 9. Publish to web
1. Hoàn thiện báo cáo, **File → Save**. Kiểm tra mọi trang không còn cảnh báo lỗi và giá trị khớp `measures.md`.
2. **Home → Publish** → đăng nhập tài khoản Power BI (tài khoản trường/cơ quan hoặc tài khoản cá nhân) → chọn **My workspace**. Dataset là dạng **Import** (ảnh chụp dữ liệu lúc nạp), không cần gateway.
3. Mở <https://app.powerbi.com> → vào báo cáo vừa publish → **File → Embed report → Publish to web (public)** → xác nhận cảnh báo → **Create embed code** → sao chép **link** (hoặc mã iframe).
4. Dán link vào báo cáo / slide. Mỗi trang dashboard đã nằm trong cùng link (người xem chuyển trang ở dưới cùng).
Lưu ý:
- **Publish to web là công khai**: ai có link đều xem được. Dữ liệu Olist là dữ liệu công khai nên chấp nhận được; **không đưa dữ liệu thật của người khác** lên.
- Một số tài khoản trường/cơ quan bị quản trị **tắt** mục *Publish to web*. Khi đó dùng tài khoản cá nhân, hoặc phương án dự phòng: xuất **PDF/PowerPoint** (File → Export) và chụp ảnh các trang.
- Muốn cập nhật sau khi có CSV mới: làm mục 10 trên máy, **Publish** lại (ghi đè báo cáo cùng tên); link public giữ nguyên.

## 10. Khi đổi máy hoặc có CSV mới
- **Đổi máy / đổi thư mục**: mở file `.pbix` → **Home → Transform data → (khung trái) Parameters → DataFolder** → sửa *Current Value* thành đường dẫn mới → **Close & Apply**. Không phải dựng lại gì.
- **Có CSV mới cùng tên file** (người chạy pipeline tải lại thư mục): ghi đè các file CSV trong thư mục, rồi **Home → Refresh**. Quan hệ, measure, visual giữ nguyên vì tên file và tên cột không đổi.
- **Có file CSV mới (bảng mới)**: tạo thêm truy vấn bằng `fnCsv` như mục 3.2 (danh sách file mới được ghi trong `exports/README.md`).

## 11. Lỗi thường gặp
| Hiện tượng | Cách xử lý |
| --- | --- |
| *DataSource.NotFound* / không tìm thấy file | `DataFolder` sai hoặc có dấu `\` ở cuối; sửa tham số (mục 10) |
| Số lệch kỳ vọng vài đồng | quên `KEEPFILTERS`/bộ lọc `Failed`, hoặc đang bật `InWindow`; so cột đúng của bảng kỳ vọng |
| Cột số hiện dạng chữ, tổng = 0 | kiểu cột chưa là Decimal/Whole number; đặt lại ở Power Query |
| Ngày hiện sai (bị đảo ngày/tháng) | quên `"en-US"` trong `fnCsv` hoặc cột ngày bị đặt kiểu text; dùng đúng Phụ lục |
| Báo *ambiguous path* | tạo thừa quan hệ; xoá hoặc chuyển Inactive (mục 4) |
| `Repeat customer rate` chạy chậm | bình thường (duyệt ~96 nghìn khách), vài giây |
| *Mark as date table* báo lỗi | còn dòng `date_key = -1` trong `dim_date`; làm lại mục 3.3 |

## Phụ lục – câu lệnh nạp từng bảng (sinh tự động)
Sinh bằng `python scripts/gen_powerbi_docs.py` từ cấu trúc bảng thật. Mỗi đoạn dán vào *Advanced Editor* của một truy vấn trống (mục 3.2).

<!-- APPENDIX:START -->
**dim_date** – Chiều thời gian (1 dòng / ngày 2016–2020 + Unknown -1)

```m
let
    Source = fnCsv("dim_date.csv", {
        {"date_key", Int64.Type}, {"full_date", type date}, {"day_of_month", Int64.Type},
        {"day_of_week", Int64.Type}, {"day_name", type text}, {"week_of_year", Int64.Type}, {"month", Int64.Type},
        {"month_name", type text}, {"quarter", Int64.Type}, {"year", Int64.Type}, {"year_month", type text},
        {"year_quarter", type text}, {"is_weekend", type logical}, {"is_holiday_br", type logical},
        {"holiday_name", type text}, {"is_black_friday", type logical}
    })
in
    Source
// dim_date: thêm bước loại dòng Unknown (date_key = -1) và cột InWindow - xem mục 3.3 của model.md
```

**dim_geography** – Chiều địa lý (1 dòng / zip)

```m
let
    Source = fnCsv("dim_geography.csv", {
        {"geography_key", Int64.Type}, {"zip_code_prefix", type text}, {"city", type text},
        {"state_code", type text}, {"state_name", type text}, {"region", type text}, {"country", type text},
        {"latitude", type number}, {"longitude", type number}
    })
in
    Source
```

**dim_customer** – Chiều khách hàng, SCD2 (1 dòng / phiên bản địa chỉ)

```m
let
    Source = fnCsv("dim_customer.csv", {
        {"customer_key", Int64.Type}, {"customer_unique_id", type text}, {"zip_code_prefix", type text},
        {"city", type text}, {"state_code", type text}, {"geography_key", Int64.Type},
        {"effective_from", type date}, {"effective_to", type date}, {"is_current", type logical},
        {"version_no", Int64.Type}
    })
in
    Source
```

**dim_seller** – Chiều seller, dùng chung bán hàng và funnel

```m
let
    Source = fnCsv("dim_seller.csv", {
        {"seller_key", Int64.Type}, {"seller_id", type text}, {"zip_code_prefix", type text}, {"city", type text},
        {"state_code", type text}, {"geography_key", Int64.Type}, {"is_from_funnel", type logical},
        {"mql_id", type text}, {"acquisition_origin", type text}, {"acquisition_channel", type text},
        {"business_segment", type text}, {"lead_type", type text}, {"business_type", type text},
        {"won_date", type date}, {"first_sale_date", type date}
    })
in
    Source
```

**dim_product** – Chiều sản phẩm

```m
let
    Source = fnCsv("dim_product.csv", {
        {"product_key", Int64.Type}, {"product_id", type text}, {"category_name_pt", type text},
        {"category_name_en", type text}, {"category_group", type text}, {"weight_g", Int64.Type},
        {"length_cm", Int64.Type}, {"height_cm", Int64.Type}, {"width_cm", Int64.Type}, {"volume_cm3", Int64.Type},
        {"size_class", type text}, {"photos_qty", Int64.Type}, {"name_length", Int64.Type},
        {"description_length", Int64.Type}
    })
in
    Source
```

**dim_order_status** – Chiều trạng thái đơn

```m
let
    Source = fnCsv("dim_order_status.csv", {
        {"order_status_key", Int64.Type}, {"order_status", type text}, {"status_group", type text},
        {"is_final", type logical}
    })
in
    Source
```

**dim_payment_type** – Chiều hình thức thanh toán

```m
let
    Source = fnCsv("dim_payment_type.csv", {
        {"payment_type_key", Int64.Type}, {"payment_type", type text}, {"payment_group", type text},
        {"display_name", type text}
    })
in
    Source
```

**dim_lead_origin** – Chiều kênh thu hút MQL

```m
let
    Source = fnCsv("dim_lead_origin.csv", {
        {"lead_origin_key", Int64.Type}, {"origin", type text}, {"channel_group", type text}
    })
in
    Source
```

**dim_lead_profile** – Chiều hồ sơ deal (junk dimension)

```m
let
    Source = fnCsv("dim_lead_profile.csv", {
        {"lead_profile_key", Int64.Type}, {"business_segment", type text}, {"lead_type", type text},
        {"lead_behaviour_profile", type text}, {"business_type", type text}, {"has_company", type text},
        {"has_gtin", type text}, {"average_stock", type text}
    })
in
    Source
```

**dim_sales_rep** – Chiều nhân viên sales (SDR / SR)

```m
let
    Source = fnCsv("dim_sales_rep.csv", {
        {"sales_rep_key", Int64.Type}, {"rep_id", type text}, {"rep_role", type text}
    })
in
    Source
```

**fact_order_item** – Fact giao dịch: 1 dòng hàng của 1 đơn

```m
let
    Source = fnCsv("fact_order_item.csv", {
        {"order_id", type text}, {"order_item_id", Int64.Type}, {"purchase_date_key", Int64.Type},
        {"shipping_limit_date_key", Int64.Type}, {"customer_key", Int64.Type},
        {"customer_geography_key", Int64.Type}, {"seller_geography_key", Int64.Type}, {"seller_key", Int64.Type},
        {"product_key", Int64.Type}, {"order_status_key", Int64.Type}, {"price", type number},
        {"freight_value", type number}, {"item_total", type number}, {"etl_batch_id", Int64.Type}
    })
in
    Source
```

**fact_order_fulfillment** – Fact accumulating snapshot: 1 đơn

```m
let
    Source = fnCsv("fact_order_fulfillment.csv", {
        {"order_id", type text}, {"customer_key", Int64.Type}, {"customer_geography_key", Int64.Type},
        {"order_status_key", Int64.Type}, {"purchase_date_key", Int64.Type}, {"approved_date_key", Int64.Type},
        {"carrier_date_key", Int64.Type}, {"delivered_date_key", Int64.Type}, {"estimated_date_key", Int64.Type},
        {"purchase_ts", type datetime}, {"approved_ts", type datetime}, {"carrier_ts", type datetime},
        {"delivered_ts", type datetime}, {"estimated_ts", type datetime}, {"approval_hours", type number},
        {"handling_days", type number}, {"transit_days", type number}, {"lead_days", type number},
        {"delay_days", Int64.Type}, {"promised_days", Int64.Type}, {"is_delivered", Int64.Type},
        {"is_late", Int64.Type}, {"is_canceled", Int64.Type}, {"item_count", Int64.Type},
        {"seller_count", Int64.Type}, {"order_value", type number}, {"freight_total", type number},
        {"payment_total", type number}, {"dq_flag_count", Int64.Type}, {"etl_batch_id", Int64.Type}
    })
in
    Source
```

**fact_payment** – Fact giao dịch: 1 lần thanh toán

```m
let
    Source = fnCsv("fact_payment.csv", {
        {"order_id", type text}, {"payment_sequential", Int64.Type}, {"purchase_date_key", Int64.Type},
        {"customer_key", Int64.Type}, {"payment_type_key", Int64.Type}, {"payment_installments", Int64.Type},
        {"payment_value", type number}, {"etl_batch_id", Int64.Type}
    })
in
    Source
```

**fact_review** – Fact giao dịch: 1 review

```m
let
    Source = fnCsv("fact_review.csv", {
        {"review_id", type text}, {"order_id", type text}, {"review_creation_date_key", Int64.Type},
        {"review_answer_date_key", Int64.Type}, {"customer_key", Int64.Type}, {"review_score", Int64.Type},
        {"is_negative", Int64.Type}, {"has_comment_title", Int64.Type}, {"has_comment_message", Int64.Type},
        {"comment_length", Int64.Type}, {"response_hours", type number}, {"delivered_late", Int64.Type},
        {"is_delivered", Int64.Type}, {"etl_batch_id", Int64.Type}
    })
in
    Source
```

**fact_lead_funnel** – Fact accumulating snapshot: 1 MQL

```m
let
    Source = fnCsv("fact_lead_funnel.csv", {
        {"mql_id", type text}, {"landing_page_id", type text}, {"first_contact_date_key", Int64.Type},
        {"won_date_key", Int64.Type}, {"first_sale_date_key", Int64.Type}, {"lead_origin_key", Int64.Type},
        {"lead_profile_key", Int64.Type}, {"seller_key", Int64.Type}, {"sdr_key", Int64.Type},
        {"sr_key", Int64.Type}, {"is_won", Int64.Type}, {"has_first_sale", Int64.Type},
        {"days_to_close", Int64.Type}, {"days_won_to_first_sale", Int64.Type},
        {"declared_product_catalog_size", type number}, {"declared_monthly_revenue", type number},
        {"seller_gmv_first_90d", type number}, {"etl_batch_id", Int64.Type}
    })
in
    Source
```

**fact_seller_monthly** – Fact periodic snapshot: 1 seller × 1 tháng

```m
let
    Source = fnCsv("fact_seller_monthly.csv", {
        {"month_date_key", Int64.Type}, {"seller_key", Int64.Type}, {"orders", Int64.Type}, {"items", Int64.Type},
        {"gmv", type number}, {"freight", type number}, {"delivered_orders", Int64.Type},
        {"late_orders", Int64.Type}, {"late_rate", type number}, {"canceled_orders", Int64.Type},
        {"avg_review_score", type number}, {"is_active", Int64.Type}, {"months_since_first_sale", Int64.Type},
        {"etl_batch_id", Int64.Type}
    })
in
    Source
```

**job_run** – Nhật ký chạy ETL từng job (cho dashboard D7)

```m
let
    Source = fnCsv("job_run.csv", {
        {"run_id", Int64.Type}, {"batch_id", Int64.Type}, {"job_name", type text}, {"layer", type text},
        {"target_table", type text}, {"started_at", type datetimezone}, {"finished_at", type datetimezone},
        {"status", type text}, {"rows_read", Int64.Type}, {"rows_inserted", Int64.Type},
        {"rows_updated", Int64.Type}, {"rows_rejected", Int64.Type}, {"message", type text}
    })
in
    Source
```

**v_run_summary** – Tóm tắt mỗi lô ETL: chế độ, thời gian, số dòng từng tầng (D7)

```m
let
    Source = fnCsv("v_run_summary.csv", {
        {"batch_id", Int64.Type}, {"mode", type text}, {"started_at", type datetimezone},
        {"finished_at", type datetimezone}, {"duration_sec", type number}, {"status", type text},
        {"source_rows", type number}, {"staging_rows", type number}, {"ods_inserted", type number},
        {"ods_rejected", type number}, {"dw_inserted", type number}, {"dw_updated", type number},
        {"staging_sec", type number}, {"ods_sec", type number}, {"dw_sec", type number}, {"test_sec", type number},
        {"mart_sec", type number}
    })
in
    Source
```

**v_dq_summary** – Kết quả kiểm thử chất lượng theo lô (D7)

```m
let
    Source = fnCsv("v_dq_summary.csv", {
        {"batch_id", Int64.Type}, {"checks", Int64.Type}, {"passed", Int64.Type}, {"failed", Int64.Type},
        {"pass_pct", type number}, {"eda_checks", Int64.Type}, {"eda_match", Int64.Type},
        {"checked_at", type datetimezone}
    })
in
    Source
```

**v_rejected_summary** – Số dòng bị loại theo lô, job, lý do (D7)

```m
let
    Source = fnCsv("v_rejected_summary.csv", {
        {"batch_id", Int64.Type}, {"job_name", type text}, {"source_table", type text}, {"reason", type text},
        {"row_count", Int64.Type}, {"last_logged_at", type datetimezone}
    })
in
    Source
```

**batch_metrics** – Chỉ số chính của kho sau mỗi lô: đơn, GMV, MQL, deal… (D7, minh hoạ funnel lấp đầy dần)

```m
let
    Source = fnCsv("batch_metrics.csv", {
        {"batch_id", Int64.Type}, {"taken_at", type datetimezone}, {"mode", type text}, {"orders", Int64.Type},
        {"order_items", Int64.Type}, {"gmv", type number}, {"mql", Int64.Type}, {"deals_won", Int64.Type},
        {"sellers_with_sale", Int64.Type}, {"customers", Int64.Type}, {"customer_versions", Int64.Type},
        {"sellers", Int64.Type}
    })
in
    Source
```

**fact_load_issue** – Khoá rơi về Unknown và khoảng thời gian âm khi nạp fact (D7)

```m
let
    Source = fnCsv("fact_load_issue.csv", {
        {"batch_id", Int64.Type}, {"fact_table", type text}, {"issue_type", type text}, {"detail", type text},
        {"row_count", Int64.Type}, {"logged_at", type datetimezone}
    })
in
    Source
```

**v_sales_daily** – Mart: GMV, đơn, AOV theo ngày (chỉ đơn không Failed)

```m
let
    Source = fnCsv("v_sales_daily.csv", {
        {"date_key", Int64.Type}, {"full_date", type date}, {"year", Int64.Type}, {"quarter", Int64.Type},
        {"year_month", type text}, {"is_weekend", type logical}, {"is_holiday_br", type logical},
        {"is_black_friday", type logical}, {"in_window", type logical}, {"orders", Int64.Type},
        {"items", Int64.Type}, {"gmv", type number}, {"freight", type number}, {"aov", type number}
    })
in
    Source
```

**v_sales_category_month** – Mart: GMV theo tháng x nhóm ngành x danh mục

```m
let
    Source = fnCsv("v_sales_category_month.csv", {
        {"year_month", type text}, {"year", Int64.Type}, {"quarter", Int64.Type}, {"in_window", type logical},
        {"category_group", type text}, {"category_name_en", type text}, {"orders", Int64.Type},
        {"items", Int64.Type}, {"gmv", type number}, {"freight", type number}, {"avg_item_price", type number}
    })
in
    Source
```

**v_sales_state_month** – Mart: GMV, freight ratio theo tháng x bang của khách

```m
let
    Source = fnCsv("v_sales_state_month.csv", {
        {"year_month", type text}, {"year", Int64.Type}, {"quarter", Int64.Type}, {"in_window", type logical},
        {"region", type text}, {"state_code", type text}, {"state_name", type text}, {"orders", Int64.Type},
        {"items", Int64.Type}, {"gmv", type number}, {"freight", type number}, {"freight_ratio", type number}
    })
in
    Source
```

**v_geo_state** – Mart địa lý: dữ liệu bản đồ theo bang (toạ độ tâm, khách, GMV, lead time, trễ)

```m
let
    Source = fnCsv("v_geo_state.csv", {
        {"state_code", type text}, {"state_name", type text}, {"region", type text}, {"latitude", type number},
        {"longitude", type number}, {"zips_with_coordinates", Int64.Type}, {"customers", Int64.Type},
        {"orders", Int64.Type}, {"gmv", type number}, {"freight_ratio", type number}, {"sellers", Int64.Type},
        {"avg_lead_days", type number}, {"late_rate_pct", type number}
    })
in
    Source
```

**v_geo_zip** – Mart địa lý: dữ liệu bản đồ theo zip có toạ độ (đơn, GMV, seller)

```m
let
    Source = fnCsv("v_geo_zip.csv", {
        {"zip_code_prefix", type text}, {"city", type text}, {"state_code", type text}, {"region", type text},
        {"latitude", type number}, {"longitude", type number}, {"customer_orders", Int64.Type},
        {"customer_gmv", type number}, {"sellers", Int64.Type}
    })
in
    Source
```

**v_category_pareto** – Mart: Pareto 80/20 GMV theo danh mục (hạng A/B/C)

```m
let
    Source = fnCsv("v_category_pareto.csv", {
        {"gmv_rank", Int64.Type}, {"category_group", type text}, {"category_name_en", type text},
        {"orders", Int64.Type}, {"items", Int64.Type}, {"gmv", type number}, {"share_pct", type number},
        {"cum_share_pct", type number}, {"abc_class", type text}
    })
in
    Source
```

**v_fulfillment_state_month** – Mart: tỷ lệ đúng hạn / hủy, thời gian từng chặng theo tháng x bang

```m
let
    Source = fnCsv("v_fulfillment_state_month.csv", {
        {"year_month", type text}, {"in_window", type logical}, {"region", type text}, {"state_code", type text},
        {"orders", Int64.Type}, {"delivered_orders", Int64.Type}, {"late_orders", Int64.Type},
        {"canceled_orders", Int64.Type}, {"on_time_rate_pct", type number}, {"cancel_rate_pct", type number},
        {"avg_lead_days", type number}, {"avg_approval_hours", type number}, {"avg_handling_days", type number},
        {"avg_transit_days", type number}, {"avg_promised_days", type number}
    })
in
    Source
```

**v_status_funnel** – Mart: số đơn đi qua từng chặng theo tháng (dạng dài)

```m
let
    Source = fnCsv("v_status_funnel.csv", {
        {"year_month", type text}, {"in_window", type logical}, {"stage_no", Int64.Type}, {"stage", type text},
        {"orders", Int64.Type}, {"pct_of_placed", type number}
    })
in
    Source
```

**v_review_vs_delay** – Mart: điểm review theo nhóm trễ giao x tháng

```m
let
    Source = fnCsv("v_review_vs_delay.csv", {
        {"year_month", type text}, {"in_window", type logical}, {"delay_bucket_no", Int64.Type},
        {"delay_bucket", type text}, {"reviews", Int64.Type}, {"score_sum", Int64.Type},
        {"negative_reviews", Int64.Type}, {"avg_score", type number}, {"pct_negative", type number},
        {"avg_response_hours", type number}
    })
in
    Source
```

**v_payment_mix_month** – Mart: cơ cấu thanh toán theo tháng x hình thức

```m
let
    Source = fnCsv("v_payment_mix_month.csv", {
        {"year_month", type text}, {"in_window", type logical}, {"payment_type", type text},
        {"payment_group", type text}, {"display_name", type text}, {"payments", Int64.Type},
        {"orders", Int64.Type}, {"payment_value", type number}, {"avg_installments", type number},
        {"value_share_pct", type number}
    })
in
    Source
```

**v_customer_rfm** – Mart: RFM từng khách thật và phân khúc

```m
let
    Source = fnCsv("v_customer_rfm.csv", {
        {"customer_unique_id", type text}, {"region", type text}, {"state_code", type text},
        {"first_purchase", type date}, {"last_purchase", type date}, {"recency_days", Int64.Type},
        {"frequency", Int64.Type}, {"monetary", type number}, {"r_score", Int64.Type}, {"f_score", Int64.Type},
        {"m_score", Int64.Type}, {"segment", type text}
    })
in
    Source
```

**v_customer_cohort** – Mart: cohort khách quay lại theo tháng mua đầu

```m
let
    Source = fnCsv("v_customer_cohort.csv", {
        {"cohort_month", type text}, {"in_window", type logical}, {"months_since", Int64.Type},
        {"cohort_size", Int64.Type}, {"customers_active", Int64.Type}, {"retention_pct", type number}
    })
in
    Source
```

**v_funnel_by_origin_month** – Mart: funnel MQL -> won -> có đơn theo tháng liên hệ x origin

```m
let
    Source = fnCsv("v_funnel_by_origin_month.csv", {
        {"first_contact_month", type text}, {"origin", type text}, {"channel_group", type text},
        {"mqls", Int64.Type}, {"won", Int64.Type}, {"won_with_sale", Int64.Type}, {"win_rate_pct", type number},
        {"won_to_sale_rate_pct", type number}, {"avg_days_to_close", type number},
        {"avg_days_won_to_first_sale", type number}, {"seller_gmv_first_90d", type number}
    })
in
    Source
```

**v_seller_scorecard** – Mart: scorecard từng seller có đơn (Pareto, cờ mẫu nhỏ)

```m
let
    Source = fnCsv("v_seller_scorecard.csv", {
        {"seller_key", Int64.Type}, {"seller_id", type text}, {"city", type text}, {"state_code", type text},
        {"region", type text}, {"is_from_funnel", type logical}, {"acquisition_channel", type text},
        {"acquisition_origin", type text}, {"business_segment", type text}, {"first_sale_date", type date},
        {"last_active_month", type date}, {"active_months", Int64.Type}, {"orders", Int64.Type},
        {"items", Int64.Type}, {"gmv", type number}, {"freight", type number}, {"delivered_orders", Int64.Type},
        {"late_orders", Int64.Type}, {"late_rate_pct", type number}, {"canceled_orders", Int64.Type},
        {"reviews", Int64.Type}, {"avg_review_score", type number}, {"pct_negative", type number},
        {"gmv_rank", Int64.Type}, {"gmv_share_pct", type number}, {"cum_share_pct", type number},
        {"abc_class", type text}, {"small_sample", type logical}
    })
in
    Source
```

**v_seller_by_channel** – Mart: seller và GMV theo kênh thu hút

```m
let
    Source = fnCsv("v_seller_by_channel.csv", {
        {"acquisition_channel", type text}, {"sellers", Int64.Type}, {"selling_sellers", Int64.Type},
        {"pct_selling", type number}, {"orders", type number}, {"gmv", type number},
        {"gmv_per_selling_seller", type number}, {"late_rate_pct", type number}, {"avg_review_score", type number},
        {"small_sample", type logical}
    })
in
    Source
```

<!-- APPENDIX:END -->
