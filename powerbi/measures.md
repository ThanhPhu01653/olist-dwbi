# Thư viện measure DAX

Dành cho người **chưa quen DAX**: mỗi measure có code để copy – dán, một dòng giải thích và định dạng hiển thị. Tên bảng và cột trong code là tên trong mô hình Power BI dựng theo `powerbi/model.md` (bảng = tên file CSV, ví dụ `fact_order_item`, `dim_date`). Các KPI bám theo `docs/DW_DESIGN.md` mục 9.

## Cách dùng
1. Mở **Model view** hoặc **Report view** → **Enter data** → tạo một bảng rỗng tên `_Measures` (chỉ để chứa measure cho gọn) → *Load*.
2. Chọn bảng `_Measures` → **Modeling → New measure** (hoặc chuột phải → *New measure*) → xoá nội dung mặc định, dán đúng code của một measure → Enter. Làm lần lượt từng measure theo thứ tự trong tài liệu (measure sau dùng measure trước).
3. Chọn measure → thẻ **Measure tools** → đặt **Format** theo dòng "Định dạng" (ví dụ *Decimal number, 2 chữ số thập phân, dấu phân cách hàng nghìn*).
4. Sau khi tạo xong, đối chiếu với bảng **giá trị kỳ vọng** ở cuối tài liệu: số trên Power BI phải khớp từng chữ số (làm tròn theo định dạng).

Quy ước:
- **GMV** chỉ tính đơn **không** thuộc nhóm trạng thái `Failed` (đơn `canceled` và `unavailable`), vì vậy nhỏ hơn tổng `price` của mọi đơn (13,49 triệu so với 13,59 triệu BRL ở toàn bộ dữ liệu). `Orders` và `AOV` dùng cùng phạm vi với GMV.
- `KEEPFILTERS(...)` giữ nguyên lựa chọn của người dùng trên bộ lọc trạng thái (nếu không có nó, điều kiện "khác Failed" sẽ ghi đè slicer).
- Ngày dùng quan hệ đang hoạt động của từng fact (ngày mua cho đơn hàng và thanh toán, ngày tạo cho review, ngày liên hệ đầu cho funnel). Muốn tính theo mốc khác, bọc bằng `USERELATIONSHIP` (mục 8).
- Bộ lọc thời gian của dashboard D1–D6: `dim_date[InWindow] = TRUE` (2017-01 → 2018-08) – xem `model.md`. Các bảng giá trị kỳ vọng cuối tài liệu cho cả hai trường hợp có và không có bộ lọc đó.

## 1. Bán hàng (nguồn: `fact_order_item`)

### GMV
```dax
GMV =
CALCULATE (
    SUM ( fact_order_item[price] ),
    KEEPFILTERS ( dim_order_status[status_group] <> "Failed" )
)
```
Tổng giá hàng của các đơn không bị hủy / không khả dụng. Định dạng: Decimal, 2 chữ số, phân cách hàng nghìn (`#,0.00`).

### Orders
```dax
Orders =
CALCULATE (
    DISTINCTCOUNT ( fact_order_item[order_id] ),
    KEEPFILTERS ( dim_order_status[status_group] <> "Failed" )
)
```
Số đơn có doanh thu (đếm mã đơn khác nhau). Định dạng: Whole number, `#,0`.

### Items
```dax
Items =
CALCULATE (
    COUNTROWS ( fact_order_item ),
    KEEPFILTERS ( dim_order_status[status_group] <> "Failed" )
)
```
Số dòng sản phẩm đã bán. Định dạng: `#,0`.

### AOV
```dax
AOV = DIVIDE ( [GMV], [Orders] )
```
Giá trị trung bình mỗi đơn (GMV chia số đơn). Định dạng: `#,0.00`.

### Freight
```dax
Freight =
CALCULATE (
    SUM ( fact_order_item[freight_value] ),
    KEEPFILTERS ( dim_order_status[status_group] <> "Failed" )
)
```
Tổng phí vận chuyển của các đơn có doanh thu. Định dạng: `#,0.00`.

### Freight ratio
```dax
Freight ratio = DIVIDE ( [Freight], [GMV] )
```
Phí vận chuyển trên giá hàng (Σ freight ÷ Σ price). Định dạng: Percentage, 1 chữ số thập phân (`0.0%`).

### Avg items per order
```dax
Avg items per order = DIVIDE ( [Items], [Orders] )
```
Số dòng hàng trung bình mỗi đơn. Định dạng: `0.00`.

### GMV by seller state (vai trò địa lý seller)
```dax
GMV by seller state =
CALCULATE (
    [GMV],
    USERELATIONSHIP ( fact_order_item[seller_geography_key], dim_geography[geography_key] )
)
```
GMV nhưng gắn theo địa lý của **seller** thay vì của khách (dùng khi dim_geography đặt ở bang của seller). Định dạng: `#,0.00`.

### GMV by shipping limit date
```dax
GMV by shipping limit date =
CALCULATE (
    [GMV],
    USERELATIONSHIP ( fact_order_item[shipping_limit_date_key], dim_date[date_key] )
)
```
GMV theo ngày hạn bàn giao cho vận chuyển (role-playing date). Định dạng: `#,0.00`.

## 2. Xử lý đơn (nguồn: `fact_order_fulfillment`)

### Orders placed
```dax
Orders placed = COUNTROWS ( fact_order_fulfillment )
```
Tổng số đơn đã đặt, mọi trạng thái. Định dạng: `#,0`.

### Failed orders
```dax
Failed orders =
CALCULATE (
    COUNTROWS ( fact_order_fulfillment ),
    KEEPFILTERS ( dim_order_status[status_group] = "Failed" )
)
```
Số đơn thuộc nhóm Failed (canceled + unavailable). Định dạng: `#,0`.

### Cancel rate
```dax
Cancel rate = DIVIDE ( [Failed orders], [Orders placed] )
```
Tỷ lệ đơn hủy / không khả dụng trên tổng đơn. Định dạng: `0.00%`.

### Delivered orders
```dax
Delivered orders = SUM ( fact_order_fulfillment[is_delivered] )
```
Số đơn đã giao (trạng thái delivered và có ngày giao). Định dạng: `#,0`.

### Late orders
```dax
Late orders = SUM ( fact_order_fulfillment[is_late] )
```
Số đơn giao trễ so với ngày dự kiến. Định dạng: `#,0`.

### On-time rate
```dax
On-time rate = DIVIDE ( [Delivered orders] - [Late orders], [Delivered orders] )
```
Tỷ lệ đơn đã giao đúng hoặc sớm hơn ngày dự kiến (`delay_days ≤ 0`). Định dạng: `0.0%`.

### Late rate
```dax
Late rate = 1 - [On-time rate]
```
Tỷ lệ đơn giao trễ. Định dạng: `0.0%`.

### Avg lead days
```dax
Avg lead days =
CALCULATE ( AVERAGE ( fact_order_fulfillment[lead_days] ), fact_order_fulfillment[is_delivered] = 1 )
```
Số ngày trung bình từ mua đến giao khách (đơn đã giao). Định dạng: `0.0`.

### Avg approval hours
```dax
Avg approval hours =
CALCULATE ( AVERAGE ( fact_order_fulfillment[approval_hours] ), fact_order_fulfillment[is_delivered] = 1 )
```
Số giờ trung bình từ mua đến duyệt thanh toán. Định dạng: `0.0`.

### Avg handling days
```dax
Avg handling days =
CALCULATE ( AVERAGE ( fact_order_fulfillment[handling_days] ), fact_order_fulfillment[is_delivered] = 1 )
```
Số ngày trung bình từ duyệt đến bàn giao cho vận chuyển (seller xử lý). Định dạng: `0.0`.

### Avg transit days
```dax
Avg transit days =
CALCULATE ( AVERAGE ( fact_order_fulfillment[transit_days] ), fact_order_fulfillment[is_delivered] = 1 )
```
Số ngày trung bình vận chuyển đến khách. Định dạng: `0.0`.

### Avg promised days
```dax
Avg promised days =
CALCULATE ( AVERAGE ( fact_order_fulfillment[promised_days] ), fact_order_fulfillment[is_delivered] = 1 )
```
Số ngày Olist hứa giao trung bình (ngày dự kiến trừ ngày mua) của các đơn đã giao. Định dạng: `0.0`.

### Avg delay days
```dax
Avg delay days =
CALCULATE ( AVERAGE ( fact_order_fulfillment[delay_days] ), fact_order_fulfillment[is_delivered] = 1 )
```
Chênh lệch ngày giao thực tế so với dự kiến (âm = giao sớm). Định dạng: `0.0`.

### Promised vs actual (days)
```dax
Promised vs actual (days) =
AVERAGEX (
    FILTER (
        fact_order_fulfillment,
        fact_order_fulfillment[is_delivered] = 1
            && NOT ISBLANK ( fact_order_fulfillment[lead_days] )
            && NOT ISBLANK ( fact_order_fulfillment[promised_days] )
    ),
    fact_order_fulfillment[promised_days] - fact_order_fulfillment[lead_days]
)
```
KPI "ngày hứa giao so với ngày giao thực tế": trung bình (số ngày hứa − số ngày thực tế); **dương = giao sớm hơn lời hứa**. Dùng cho D3. Định dạng: `0.0`.

### Early delivery rate
```dax
Early delivery rate =
DIVIDE (
    CALCULATE ( COUNTROWS ( fact_order_fulfillment ), fact_order_fulfillment[is_delivered] = 1, fact_order_fulfillment[delay_days] < 0 ),
    [Delivered orders]
)
```
Tỷ lệ đơn giao sớm hơn ngày dự kiến. Định dạng: `0.0%`.

### Delivered orders by delivery date
```dax
Delivered orders by delivery date =
CALCULATE ( [Delivered orders], USERELATIONSHIP ( fact_order_fulfillment[delivered_date_key], dim_date[date_key] ) )
```
Số đơn tính theo **ngày giao** thay vì ngày mua (role-playing date). Định dạng: `#,0`.

## 3. Thanh toán (nguồn: `fact_payment`)

### Payment value
```dax
Payment value = SUM ( fact_payment[payment_value] )
```
Tổng giá trị thanh toán (BRL). Định dạng: `#,0.00`.

### Payments
```dax
Payments = COUNTROWS ( fact_payment )
```
Số lần thanh toán. Định dạng: `#,0`.

### Avg installments
```dax
Avg installments = AVERAGE ( fact_payment[payment_installments] )
```
Số kỳ trả góp trung bình. Định dạng: `0.00`.

### Payment share
```dax
Payment share =
DIVIDE ( [Payment value], CALCULATE ( [Payment value], ALL ( dim_payment_type ) ) )
```
Tỷ trọng giá trị của một hình thức thanh toán trong tổng (đặt `dim_payment_type[display_name]` lên trục). Định dạng: `0.0%`.

## 4. Review và khách hàng (nguồn: `fact_review`, `fact_order_fulfillment`)

### Reviews
```dax
Reviews = COUNTROWS ( fact_review )
```
Số review. Định dạng: `#,0`.

### Avg review
```dax
Avg review = AVERAGE ( fact_review[review_score] )
```
Điểm review trung bình (1–5). Định dạng: `0.00`.

### % negative
```dax
% negative = DIVIDE ( SUM ( fact_review[is_negative] ), [Reviews] )
```
Tỷ lệ review tiêu cực (điểm ≤ 2). Định dạng: `0.0%`.

### Avg review - late delivery
```dax
Avg review - late delivery = CALCULATE ( [Avg review], fact_review[delivered_late] = 1 )
```
Điểm trung bình của các đơn giao trễ. Định dạng: `0.00`.

### Avg review - on time
```dax
Avg review - on time = CALCULATE ( [Avg review], fact_review[delivered_late] = 0 )
```
Điểm trung bình của các đơn không trễ. Định dạng: `0.00`.

### Customers
```dax
Customers =
COUNTROWS (
    FILTER ( VALUES ( dim_customer[customer_unique_id] ), CALCULATE ( COUNTROWS ( fact_order_fulfillment ) ) > 0 )
)
```
Số khách thật (theo `customer_unique_id`, không đếm các phiên bản địa chỉ SCD2) có ít nhất một đơn. Chạy vài giây vì duyệt gần 100 nghìn khách. Định dạng: `#,0`.

### Repeat customers
```dax
Repeat customers =
COUNTROWS (
    FILTER ( VALUES ( dim_customer[customer_unique_id] ), CALCULATE ( COUNTROWS ( fact_order_fulfillment ) ) >= 2 )
)
```
Số khách có từ 2 đơn trở lên (mọi trạng thái). Định dạng: `#,0`.

### Repeat customer rate
```dax
Repeat customer rate = DIVIDE ( [Repeat customers], [Customers] )
```
Tỷ lệ khách quay lại mua (≥ 2 đơn ÷ tổng khách). Định dạng: `0.00%`.

## 5. Thu hút seller (nguồn: `fact_lead_funnel`)
Trục thời gian của nhóm này là **tháng liên hệ đầu** của MQL (quan hệ đang hoạt động), nên các tỷ lệ là tỷ lệ của "nhóm MQL liên hệ trong tháng đó".

### MQLs
```dax
MQLs = COUNTROWS ( fact_lead_funnel )
```
Số khách tiềm năng (MQL). Định dạng: `#,0`.

### Won deals
```dax
Won deals = SUM ( fact_lead_funnel[is_won] )
```
Số MQL đã được chốt thành seller. Định dạng: `#,0`.

### MQL to won rate
```dax
MQL to won rate = DIVIDE ( [Won deals], [MQLs] )
```
Tỷ lệ chuyển đổi MQL → seller (đã chốt). Định dạng: `0.0%`.

### Avg days to close
```dax
Avg days to close = AVERAGE ( fact_lead_funnel[days_to_close] )
```
Số ngày trung bình từ liên hệ đầu đến chốt deal (chỉ các deal đã chốt). Định dạng: `0.0`.

### Sellers with first sale
```dax
Sellers with first sale = SUM ( fact_lead_funnel[has_first_sale] )
```
Số seller đã chốt và đã có đơn hàng. Định dạng: `#,0`.

### Won to first sale rate
```dax
Won to first sale rate = DIVIDE ( [Sellers with first sale], [Won deals] )
```
Tỷ lệ seller đã chốt mà có đơn đầu tiên. Định dạng: `0.0%`.

### Avg days won to first sale
```dax
Avg days won to first sale = AVERAGE ( fact_lead_funnel[days_won_to_first_sale] )
```
Số ngày trung bình từ chốt deal đến đơn đầu tiên. Định dạng: `0.0`.

### Seller GMV first 90d
```dax
Seller GMV first 90d = SUM ( fact_lead_funnel[seller_gmv_first_90d] )
```
GMV của các seller từ funnel trong 90 ngày đầu kể từ đơn đầu tiên. Định dạng: `#,0.00`.

### Won deals by won date
```dax
Won deals by won date =
CALCULATE ( [Won deals], USERELATIONSHIP ( fact_lead_funnel[won_date_key], dim_date[date_key] ) )
```
Số deal tính theo **ngày chốt** (role-playing date) – dùng để xem deal chốt mỗi tháng. Định dạng: `#,0`.

## 6. Hiệu suất seller (nguồn: `fact_seller_monthly`)

### Active sellers
```dax
Active sellers =
CALCULATE ( DISTINCTCOUNT ( fact_seller_monthly[seller_key] ), fact_seller_monthly[is_active] = 1 )
```
Số seller có ít nhất một đơn trong kỳ đang chọn. Định dạng: `#,0`.

### Seller GMV (monthly)
```dax
Seller GMV (monthly) = SUM ( fact_seller_monthly[gmv] )
```
Tổng GMV từ bảng seller-tháng (bằng `GMV` khi cùng phạm vi thời gian). Định dạng: `#,0.00`.

### Seller late rate
```dax
Seller late rate =
DIVIDE ( SUM ( fact_seller_monthly[late_orders] ), SUM ( fact_seller_monthly[delivered_orders] ) )
```
Tỷ lệ giao trễ tính trên bảng seller-tháng. Định dạng: `0.0%`.

### Small sample warning
```dax
Small sample warning =
IF ( [Active sellers] < 30, "⚠ Mẫu nhỏ (dưới 30 seller)", "" )
```
Hiện cảnh báo khi một nhóm (ví dụ kênh thu hút) có quá ít seller để kết luận. Định dạng: Text.

## 7. So sánh theo thời gian (cần `dim_date` đã Mark as date table)

### GMV last month
```dax
GMV last month = CALCULATE ( [GMV], DATEADD ( dim_date[full_date], -1, MONTH ) )
```
GMV của tháng liền trước. Định dạng: `#,0.00`.

### GMV MoM %
```dax
GMV MoM % = DIVIDE ( [GMV] - [GMV last month], [GMV last month] )
```
Tăng trưởng so với tháng trước. Định dạng: `+0.0%;-0.0%;0.0%`.

### GMV last year
```dax
GMV last year = CALCULATE ( [GMV], SAMEPERIODLASTYEAR ( dim_date[full_date] ) )
```
GMV cùng kỳ năm trước. Định dạng: `#,0.00`.

### GMV YoY %
```dax
GMV YoY % = DIVIDE ( [GMV] - [GMV last year], [GMV last year] )
```
Tăng trưởng so với cùng kỳ năm trước. Định dạng: `+0.0%;-0.0%;0.0%`.

### GMV YTD
```dax
GMV YTD = TOTALYTD ( [GMV], dim_date[full_date] )
```
GMV luỹ kế từ đầu năm. Định dạng: `#,0.00`.

### Orders MoM %
```dax
Orders MoM % =
DIVIDE ( [Orders] - CALCULATE ( [Orders], DATEADD ( dim_date[full_date], -1, MONTH ) ), CALCULATE ( [Orders], DATEADD ( dim_date[full_date], -1, MONTH ) ) )
```
Tăng trưởng số đơn so với tháng trước. Định dạng: `+0.0%;-0.0%;0.0%`.

Lưu ý: dữ liệu bắt đầu thưa từ 2016, nên MoM của 01/2017 và YoY của 2017 không có ý nghĩa (kỳ so sánh gần như trống); dashboard chỉ nên so sánh trong cửa sổ 2017-01 → 2018-08.

## 8. Role-playing date: khi nào dùng `USERELATIONSHIP`
Mỗi fact có một quan hệ ngày **đang hoạt động** (ngày mua / ngày tạo review / ngày liên hệ đầu); các quan hệ ngày còn lại là **không hoạt động** (nét đứt trong Model view). Muốn một measure tính theo mốc khác, bọc nó trong `CALCULATE ( <measure>, USERELATIONSHIP ( <cột khoá ngày của fact>, dim_date[date_key] ) )` như các measure *by shipping limit date*, *by delivery date*, *by won date* ở trên. Các cột khoá: `fact_order_fulfillment` có `approved_date_key`, `carrier_date_key`, `delivered_date_key`, `estimated_date_key`; `fact_review` có `review_answer_date_key`; `fact_lead_funnel` có `won_date_key`, `first_sale_date_key`.

## 9. Measure cảnh báo cho conditional formatting
Cách dùng: chọn visual → **Format → Cell elements** (bảng / ma trận) hoặc **Data colors / Callout value** (thẻ, cột) → nút **fx** → *Format style* = **Field value** → chọn measure màu tương ứng. Màu lấy từ `powerbi/theme.json` (xanh = tốt, vàng = cần chú ý, đỏ = xấu). Ngưỡng là đề xuất; sửa ngưỡng ngay trong code nếu nhóm quyết định khác.

```dax
Color On-time rate =
SWITCH ( TRUE (), ISBLANK ( [On-time rate] ), "#8A94A6", [On-time rate] < 0.90, "#D64545", [On-time rate] < 0.95, "#E0A100", "#2E9E6B" )
```
On-time rate dưới 90% → đỏ; dưới 95% → vàng; còn lại xanh.

```dax
Color Avg review =
SWITCH ( TRUE (), ISBLANK ( [Avg review] ), "#8A94A6", [Avg review] < 3.8, "#D64545", [Avg review] < 4.2, "#E0A100", "#2E9E6B" )
```
Điểm review dưới 3,8 → đỏ; dưới 4,2 → vàng.

```dax
Color % negative =
SWITCH ( TRUE (), ISBLANK ( [% negative] ), "#8A94A6", [% negative] > 0.20, "#D64545", [% negative] > 0.12, "#E0A100", "#2E9E6B" )
```
Tỷ lệ review tiêu cực trên 20% → đỏ; trên 12% → vàng.

```dax
Color Cancel rate =
SWITCH ( TRUE (), ISBLANK ( [Cancel rate] ), "#8A94A6", [Cancel rate] > 0.02, "#D64545", [Cancel rate] > 0.01, "#E0A100", "#2E9E6B" )
```
Tỷ lệ hủy trên 2% → đỏ; trên 1% → vàng.

```dax
Color Freight ratio =
SWITCH ( TRUE (), ISBLANK ( [Freight ratio] ), "#8A94A6", [Freight ratio] > 0.25, "#D64545", [Freight ratio] > 0.18, "#E0A100", "#2E9E6B" )
```
Phí vận chuyển trên giá hàng trên 25% → đỏ; trên 18% → vàng.

```dax
Color growth =
VAR g = [GMV MoM %]
RETURN SWITCH ( TRUE (), ISBLANK ( g ), "#8A94A6", g < 0, "#D64545", "#2E9E6B" )
```
Tăng trưởng GMV so với tháng trước: âm → đỏ, dương → xanh.

```dax
Color promised vs actual =
VAR d = [Promised vs actual (days)]
RETURN SWITCH ( TRUE (), ISBLANK ( d ), "#8A94A6", d < 0, "#D64545", d < 5, "#E0A100", "#2E9E6B" )
```
Giao thực tế chậm hơn lời hứa → đỏ; sớm dưới 5 ngày → vàng; sớm từ 5 ngày → xanh.

Cảnh báo bằng chữ (dùng làm tiêu đề phụ hoặc thẻ):
```dax
Alert text =
VAR msgs =
    IF ( [On-time rate] < 0.90, "On-time rate dưới 90%. ", "" )
        & IF ( [Avg review] < 3.8, "Điểm review dưới 3,8. ", "" )
        & IF ( [Cancel rate] > 0.02, "Tỷ lệ hủy trên 2%. ", "" )
RETURN IF ( msgs = "", "Các chỉ số chính trong ngưỡng", "⚠ " & msgs )
```
Gom các cảnh báo chính thành một dòng chữ. Định dạng: Text.

---

## 10. Bảng giá trị kỳ vọng (tính bằng SQL trên trạng thái cuối của `olist_dw`)
Dùng để đối chiếu số trên Power BI: đặt các slicer/bộ lọc giống cột bên dưới rồi so với giá trị của measure. Cột **Toàn bộ dữ liệu** = không đặt bộ lọc thời gian nào (trên Power BI: bỏ lọc `InWindow`). Số được sinh bằng `python scripts/gen_powerbi_docs.py` từ database nên luôn đúng với dữ liệu hiện tại; nếu sau này nạp lại dữ liệu, chạy lại script để cập nhật.

<!-- EXPECTED:START -->
| Measure | Toàn bộ dữ liệu | Cửa sổ 2017-01 → 2018-08 | Năm 2017 | Tháng 2017-11 |
| --- | ---: | ---: | ---: | ---: |
| GMV | 13,494,400.74 | 13,449,529.68 | 6,108,492.27 | 1,003,862.14 |
| Orders | 98,199 | 97,905 | 44,375 | 7,421 |
| Items | 112,101 | 111,752 | 50,617 | 8,626 |
| AOV | 137.42 | 137.37 | 137.66 | 135.27 |
| Freight | 2,241,126.29 | 2,234,177.06 | 982,076.97 | 168,329.54 |
| Freight ratio | 16.6% | 16.6% | 16.1% | 16.8% |
| Orders placed | 99,441 | 99,092 | 45,101 | 7,544 |
| Failed orders | 1,234 | 1,182 | 722 | 121 |
| Cancel rate | 1.24% | 1.19% | 1.60% | 1.60% |
| Delivered orders | 96,470 | 96,203 | 43,426 | 7,288 |
| Late orders | 6,534 | 6,531 | 2,453 | 904 |
| On-time rate | 93.2% | 93.2% | 94.4% | 87.6% |
| Early delivery rate | 91.9% | 91.9% | 93.4% | 85.7% |
| Avg lead days | 12.6 | 12.5 | 13.0 | 15.2 |
| Avg approval hours | 10.3 | 10.2 | 10.1 | 10.8 |
| Avg handling days | 2.9 | 2.8 | 3.0 | 3.6 |
| Avg transit days | 9.3 | 9.3 | 9.6 | 11.1 |
| Avg promised days | 24.4 | 24.3 | 25.3 | 23.2 |
| Avg delay days | -11.9 | -11.8 | -12.3 | -8.1 |
| Promised vs actual (days) | 11.8 | 11.7 | 12.3 | 8.0 |
| Payment value | 16,008,872.12 | 15,944,480.57 | 7,249,746.73 | 1,194,882.80 |
| Payments | 103,886 | 103,520 | 47,525 | 7,863 |
| Avg installments | 2.85 | 2.85 | 3.00 | 3.02 |
| Reviews | 99,224 | 98,899 | 42,735 | 4,786 |
| Avg review | 4.09 | 4.09 | 4.11 | 4.11 |
| % negative | 14.7% | 14.6% | 13.9% | 13.4% |
| Avg review - late delivery | 2.27 | 2.27 | 2.35 | 2.63 |
| Avg review - on time | 4.21 | 4.21 | 4.20 | 4.18 |
| Customers | 96,096 | 95,774 | 43,713 | 7,430 |
| Repeat customers | 2,997 | 2,975 | 1,256 | 109 |
| Repeat customer rate | 3.12% | 3.11% | 2.87% | 1.47% |
| MQLs (theo tháng liên hệ đầu) | 8,000 | 8,000 | 2,002 | 445 |
| Won deals | 842 | 842 | 61 | 18 |
| MQL to won rate | 10.5% | 10.5% | 3.0% | 4.0% |
| Avg days to close | 48.5 | 48.5 | 212.2 | 155.1 |
| Sellers with first sale | 380 | 380 | 19 | 6 |
| Won to first sale rate | 45.1% | 45.1% | 31.1% | 33.3% |
| Avg days won to first sale | 51.8 | 51.8 | 42.9 | 42.8 |
| Seller GMV first 90d | 538,271.72 | 538,271.72 | 19,413.78 | 2,085.32 |
| Active sellers (fact_seller_monthly) | 3,095 | 3,068 | 1,784 | 965 |
| Seller GMV (monthly) | 13,494,400.74 | 13,449,529.68 | 6,108,492.27 | 1,003,862.14 |
| Seller late rate | 6.7% | 6.7% | 5.6% | 12.3% |

Ghi chú: dòng *Tháng 2017-11* và các cột có lọc thời gian áp dụng cho ngày mua (đơn, thanh toán), ngày tạo review (review), tháng liên hệ đầu (funnel), tháng (seller-tháng). Bộ lọc tương ứng trên Power BI: slicer `dim_date[year_month]` hoặc bộ lọc trang `InWindow = TRUE`.

**So sánh theo thời gian (GMV)**

| Tháng đang chọn | GMV | GMV last month | GMV MoM % | GMV last year | GMV YoY % |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2017-11 | 1,003,862.14 | 660,179.62 | +52.1% | 0.00 | (trống) |
| 2018-05 | 992,871.75 | 993,592.98 | -0.1% | 503,159.19 | +97.3% |
| 2018-08 | 848,860.10 | 878,044.27 | -3.3% | 568,245.79 | +49.4% |
<!-- EXPECTED:END -->
