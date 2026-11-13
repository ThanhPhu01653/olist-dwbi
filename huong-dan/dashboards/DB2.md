# DB2 – Giao hàng và trải nghiệm khách

*Loại: Vận hành và thống kê (Key Influencers). Người dựng: Người 2 (Phú dựng file gốc, tổng hợp và chỉnh sửa). Dựng theo `powerbi/model.md` (mục 8); công thức DAX ở `powerbi/measures.md`. Cây phân tích: `huong-dan/05-nghiep-vu-nhap.md` mục 6 (hình `figures/2-3_cay_phan_tich_DB2.png`).*

## 1. Mục tiêu

Theo dõi chu trình xử lý đơn (mỗi chặng mất bao lâu, vùng nào chậm, lời hứa giao có sát thực tế không), hiểu trải nghiệm khách (điểm review, ảnh hưởng của giao trễ, thanh toán, khách quay lại) và dùng Key Influencers để chỉ ra yếu tố đi kèm review tiêu cực.

## 2. Câu hỏi trả lời, người dùng và tần suất xem

- Đơn mất bao lâu ở từng chặng (duyệt → bàn giao → giao)?
- Tỷ lệ giao trễ và hủy là bao nhiêu, vùng/bang nào chậm nhất?
- Ngày hứa giao so với ngày giao thực tế chênh bao nhiêu?
- Điểm review TB bao nhiêu, bao nhiêu % tiêu cực?
- Giao trễ làm điểm review giảm thế nào?
- Khách thanh toán bằng gì, trả góp bao nhiêu kỳ?
- Bao nhiêu khách quay lại; phân khúc RFM và cohort?

| Người dùng | Câu hỏi | Tần suất xem |
| --- | --- | --- |
| Quản lý vận hành và logistics | Chặng nào chậm; bang nào trễ nhiều; ngày hứa so với thực tế? | hằng ngày đến hằng tuần |
| Chăm sóc khách hàng | Vì sao review thấp; khách nào quay lại; thanh toán ra sao? | hằng tuần |

## 3. Bố cục từng trang

Trang 16:9 chia 12 cột; số hàng là thứ tự từ trên xuống. Mỗi dòng là một visual. Bộ lọc trang `dim_date[InWindow] = TRUE` (2017-01 → 2018-08).

### Trang 1 – Giao hàng

| Hàng | Cột (trong 12) | Visual | Trường / measure |
| --- | --- | --- | --- |
| 1 | 1–3 | Card | On-time rate (`Color On-time rate`) |
| 1 | 4–6 | Card | Avg lead days |
| 1 | 7–9 | Card | Avg promised days |
| 1 | 10–12 | Card | Promised vs actual (days) (`Color promised vs actual`) |
| 2 | 1–4 | Funnel | bảng `v_status_funnel` (lọc `in_window`): `stage` (sắp theo `stage_no`) → `orders` |
| 2 | 5–12 | Stacked column | trục `year_month`; giá trị `Avg handling days`, `Avg transit days` (và `Avg approval hours` ở trục phụ hoặc đổi sang ngày) |
| 3 | 1–6 | Map hoặc bar chart | `Late rate` theo `dim_geography[state_code]`, màu theo `Color On-time rate` |
| 3 | 7–12 | Clustered column | `Avg promised days` và `Avg lead days` theo `dim_geography[region]` |
| 4 | 1–6 | Column | số đơn theo cột tính toán `fact_order_fulfillment[Delay bucket]` |
| 4 | 7–12 | Table | bang, đơn đã giao, `Late rate`, `Avg lead days`, `Cancel rate` (conditional formatting) |

### Trang 2 – Trải nghiệm khách

| Hàng | Cột (trong 12) | Visual | Trường / measure |
| --- | --- | --- | --- |
| 1 | 1–3 | Card | Avg review (`Color Avg review`) |
| 1 | 4–6 | Card | % negative (`Color % negative`) |
| 1 | 7–9 | Card | Repeat customer rate |
| 1 | 10–12 | Card | Avg installments |
| 2 | 1–6 | Clustered column | bảng `v_review_vs_delay`: trục `delay_bucket` (sắp theo `delay_bucket_no`), giá trị `avg_score` |
| 2 | 7–12 | Column | `fact_review[review_score]` → `Reviews` (phân bố 1–5 sao) |
| 3 | 1–4 | Donut | `dim_payment_type[display_name]` → `Payment value` |
| 3 | 5–8 | Bar chart | bảng `v_customer_rfm`: `segment` → đếm `customer_unique_id` |
| 3 | 9–12 | Matrix (heatmap) | bảng `v_customer_cohort`: hàng `cohort_month`, cột `months_since`, giá trị `retention_pct` (color scale) |

### Trang 3 – Yếu tố ảnh hưởng đến review tiêu cực (Key Influencers)

| Hàng | Cột (trong 12) | Visual | Trường / measure |
| --- | --- | --- | --- |
| 1 | 1–9 | Key influencers (visual AI) | *Analyze* `fact_review[Review type]` = **Tiêu cực**; *Explain by* `fact_review[delivered_late]`, `Delay days (order)`, `Lead days (order)`, `Promised days (order)`, `Freight (order)`, `Order value (order)`, `Item count (order)`, `fact_review[has_comment_message]`, `dim_customer[state_code]`, `dim_date[year_quarter]` |
| 1 | 10–12 | Card ×3 | `% negative`; `Avg review - late delivery`; `Avg review - on time` |
| 2 | 1–12 | Văn bản | chú thích: "mô hình thống kê tự động, cho thấy yếu tố đi kèm review tiêu cực, không chứng minh nhân quả" |

### Trang tooltip `Tooltip_Muc_tre`

| Hàng | Cột (trong 12) | Visual | Trường / measure |
| --- | --- | --- | --- |
| 1 | 1–12 | Card + cột | số review, điểm TB, % tiêu cực theo nhóm trễ (gán vào cột `v_review_vs_delay`) |

## 4. Visual, measure, slicer

**KPI và measure dùng**

| Measure | Ý nghĩa |
| --- | --- |
| **On-time rate / Late rate** | đúng hạn / trễ |
| **Avg lead days** | mua → giao |
| **Avg approval hours** | mua → duyệt |
| **Avg handling days** | duyệt → bàn giao |
| **Avg transit days** | bàn giao → giao |
| **Avg promised days** | số ngày hứa giao |
| **Promised vs actual (days)** | **KPI ngày hứa giao so với thực tế** (dương = giao sớm hơn lời hứa) |
| **Early delivery rate** | đơn giao sớm hơn dự kiến |
| **Cancel rate** | tỷ lệ hủy |
| **Avg review** | điểm review TB |
| **% negative** | % review tiêu cực (≤ 2 điểm) |
| **Avg review - late delivery / on time** | điểm TB đơn trễ / không trễ |
| **Payment value / Payment share** | giá trị và tỷ trọng thanh toán |
| **Avg installments** | số kỳ trả góp |
| **Repeat customer rate** | khách quay lại (≥ 2 đơn) |

Mã DAX đầy đủ từng measure: `powerbi/measures.md`. Màu cảnh báo: các measure `Color …` ở mục 6 của file đó.

**Slicer và bộ lọc**

- `dim_date[year_month]`
- `dim_geography[region]`
- `dim_order_status[order_status]`
- `dim_product[category_group]` (tuỳ chọn)
- `dim_payment_type[payment_group]`
- Slicer thời gian dạng phân cấp `dim_date` Năm → Quý → Tháng và slicer địa lý Vùng → Bang
- Bộ lọc trang `dim_date[InWindow] = TRUE` (2017-01 → 2018-08).

## 5. Drill-down, drill-through, tooltip

- Bản đồ / bảng: hierarchy Geography (vùng → bang → thành phố)
- Drill-through sang trang chi tiết đơn (tuỳ chọn)
- Cohort: drill từ năm xuống tháng
- Bảng RFM: drill-through sang danh sách khách (ẩn mã nếu cần)
- Key Influencers: thêm 7 cột tính toán vào `fact_review` bằng `LOOKUPVALUE` theo `order_id` (mã DAX ở `powerbi/model.md` mục 8, DB2 trang 3). Kỳ vọng từ khám phá dữ liệu: giao trễ là yếu tố liên hệ mạnh nhất với review tiêu cực (Cramér's V 0,403; η của điểm review theo cờ trễ 0,392); sau khi dựng, ghi các yếu tố đứng đầu mà visual trả về vào báo cáo.
- Tooltip: gán `Tooltip_Muc_tre` cho cột điểm review theo nhóm trễ; gán một tooltip theo bang (Late rate, Avg lead days, Orders) cho bản đồ ở trang 1.

## 6. Định dạng có điều kiện và DAX đặc biệt

- Card và bảng: màu theo `Color On-time rate`, `Color Cancel rate`, `Color promised vs actual`
- Bản đồ: thang màu từ xanh đến đỏ theo `Late rate`
- Card review: theo `Color Avg review`, `Color % negative`
- Cohort: **color scale** trắng → xanh đậm
- Cột `avg_score` theo nhóm trễ: màu đỏ nếu < 3

**KPI ngày hứa giao so với thực tế**

```dax
Promised vs actual (days) =
AVERAGEX ( FILTER ( fact_order_fulfillment, fact_order_fulfillment[is_delivered] = 1
    && NOT ISBLANK ( fact_order_fulfillment[lead_days] ) && NOT ISBLANK ( fact_order_fulfillment[promised_days] ) ),
    fact_order_fulfillment[promised_days] - fact_order_fulfillment[lead_days] )
```

**Role-playing date: đơn theo ngày giao**

```dax
Delivered orders by delivery date =
CALCULATE ( [Delivered orders], USERELATIONSHIP ( fact_order_fulfillment[delivered_date_key], dim_date[date_key] ) )
```

**Tách điểm review theo giao trễ**

```dax
Avg review - late delivery = CALCULATE ( [Avg review], fact_review[is_delivered] = 1, fact_review[delivered_late] = 1 )
Avg review - on time = CALCULATE ( [Avg review], fact_review[is_delivered] = 1, fact_review[delivered_late] = 0 )
```

**Khách quay lại**

```dax
Repeat customers =
COUNTROWS ( FILTER ( VALUES ( dim_customer[customer_unique_id] ), CALCULATE ( COUNTROWS ( fact_order_fulfillment ) ) >= 2 ) )
```

## 7. Đáp ứng checklist

Checklist chung ở [`README.md`](README.md); ma trận mục × dashboard ở đó.

| Mục checklist | Đáp ứng | Cách đáp ứng trong DB2 |
| --- | --- | --- |
| Định dạng số | ✓ | xem bảng định dạng bên dưới |
| Tiêu đề dạng câu hỏi | ✓ | xem danh sách tiêu đề bên dưới |
| Màu đỏ chỉ để cảnh báo | ✓ | mục 6: đỏ chỉ ở định dạng có điều kiện (trễ, hủy, điểm review thấp) |
| Định dạng có điều kiện | ✓ | Card On-time rate, Cancel rate, Avg review; bản đồ Late rate; cohort color scale |
| Slicer phân cấp | ✓ | slicer Năm → Quý → Tháng và Vùng → Bang |
| OLAP drill-down / roll-up | ✓ | bản đồ / bảng Geography Vùng → Bang → Thành phố; cohort năm → tháng |
| Drill-through | – | không áp dụng (drill-through nằm ở DB3, DB4) |
| Tooltip | ✓ | `Tooltip_Muc_tre` và tooltip theo bang |
| Chuỗi thời gian có dự báo | – | không áp dụng (dự báo ở DB1) |
| Thống kê: Key Influencers | ✓ | trang 3: visual Key influencers cho `Review type` = Tiêu cực |
| Publish web và mã QR | ✓ | cùng báo cáo với các dashboard khác |

**Định dạng số** (*Measure tools → Format → Custom* hoặc *Display units* của visual):

| Chỉ số | Loại | Định dạng |
| --- | --- | --- |
| Avg lead days, Avg promised days, Promised vs actual | ngày | `0.0` → 12.6 |
| On-time rate, Late rate, Cancel rate, % negative, Repeat customer rate | phần trăm | `0.0%` |
| Orders placed, Reviews | số | `#,0.0,"K"` |
| Avg review | điểm | `0.00` |
| Payment value | tiền | `#,0.0,,"M"` |
| Avg installments | số kỳ | `0.0` |

**Tiêu đề visual dạng câu hỏi** (lấy từ mục 2; mỗi visual chọn một câu phù hợp làm tiêu đề):

- Đơn mất bao lâu ở từng chặng (duyệt → bàn giao → giao)?
- Tỷ lệ giao trễ và hủy là bao nhiêu, vùng/bang nào chậm nhất?
- Ngày hứa giao so với ngày giao thực tế chênh bao nhiêu?
- Điểm review TB bao nhiêu, bao nhiêu % tiêu cực?
- Giao trễ làm điểm review giảm thế nào?
- Khách thanh toán bằng gì, trả góp bao nhiêu kỳ?
- Bao nhiêu khách quay lại; phân khúc RFM và cohort?

## 8. Insight gợi ý (có số thật, để viết vào báo cáo và slide)

1. Olist **hứa TB 24,4 ngày nhưng giao thực tế 12,6 ngày**: giao sớm hơn lời hứa 11,8 ngày, 91,9% đơn giao sớm hơn dự kiến → "đúng hạn" 93,2% dễ đạt vì ngày dự kiến quá rộng.
2. Chặng dài nhất là **vận chuyển (9,3 ngày)**, bàn giao của seller 2,9 ngày, duyệt 10,3 giờ.
3. **Nordeste trễ nhiều nhất (12,8%)**, Sudeste 6,1%; Norte có lead time dài nhất (22,6 ngày so với 10,7 ngày ở Sudeste). Bang MA trễ 17,4%.
4. Đúng hạn tụt từ 95,8% (10/2017) xuống **87,6% (11/2017, Black Friday)** và 81,0% (03/2018): đợt cao điểm làm vận chuyển quá tải.
5. Tỷ lệ hủy / không khả dụng toàn sàn chỉ 1,24% (1.234 đơn).
6. **Điểm review tụt theo mức trễ: 4,29 (giao sớm) → 3,29 (trễ 1–3 ngày) → 2,10 (4–7) → 1,70 (trên 7 ngày)**; % tiêu cực tăng 9,2% → 79,2%.
7. Đơn trễ chỉ chiếm 6,5% số review nhưng tạo **27,4% số review tiêu cực** (4.000/14.575).
8. Thẻ tín dụng chiếm **78,3% giá trị thanh toán**, boleto 17,9%; thẻ trả góp TB 3,5 kỳ và 66,9% giao dịch thẻ trả góp nhiều kỳ.
9. Chỉ **3,12% khách mua lại** (2.997/96.096); cohort cho thấy tỷ lệ quay lại sau 1 tháng chỉ ~0,5%.
10. RFM: 94.983 khách; "Ngủ đông" 36.957 và "Khách mới" 36.752 chiếm gần hết; chỉ 129 khách Champions.
11. **Key Influencers** (kỳ vọng, cần xác nhận sau khi dựng): giao trễ đứng đầu các yếu tố đi kèm review tiêu cực; theo khám phá dữ liệu, tỷ lệ review tiêu cực là 12,8% ở đơn đã giao so với 76,7% ở đơn hủy (số trong `handoff/2026-11-14-P8-eda.md`).

Lưu ý: 1.359 đơn có `carrier_before_approved` (bàn giao trước khi duyệt) nên `handling_days` của các đơn này để trống; cờ lỗi nằm ở `etl_log.fact_load_issue`.

## 9. Bảng giá trị kỳ vọng (SQL trên trạng thái cuối, để đối chiếu số trên Power BI)

Cột **Cửa sổ 2017-01 → 2018-08** là số khi bật bộ lọc trang `InWindow`; cột **Toàn bộ dữ liệu** khi bỏ lọc. Sinh bởi `python scripts/gen_powerbi_docs.py` rồi chạy lại `python scripts/gen_dashboard_docs.py`.

| Measure | Toàn bộ dữ liệu | Cửa sổ 2017-01 → 2018-08 | Năm 2017 | Tháng 2017-11 |
| --- | ---: | ---: | ---: | ---: |
| Orders placed | 99,441 | 99,092 | 45,101 | 7,544 |
| Failed orders | 1,234 | 1,182 | 722 | 121 |
| Cancel rate | 1.24% | 1.19% | 1.60% | 1.60% |
| Delivered orders | 96,470 | 96,203 | 43,426 | 7,288 |
| Late orders | 6,534 | 6,531 | 2,453 | 904 |
| Late rate | 6.8% | 6.8% | 5.6% | 12.4% |
| On-time rate | 93.2% | 93.2% | 94.4% | 87.6% |
| Early delivery rate | 91.9% | 91.9% | 93.4% | 85.7% |
| Avg lead days | 12.6 | 12.5 | 13.0 | 15.2 |
| Avg approval hours | 10.3 | 10.2 | 10.1 | 10.8 |
| Avg handling days | 2.9 | 2.8 | 3.0 | 3.6 |
| Avg transit days | 9.3 | 9.3 | 9.6 | 11.1 |
| Avg promised days | 24.4 | 24.3 | 25.3 | 23.2 |
| Avg delay days | -11.9 | -11.8 | -12.3 | -8.1 |
| Promised vs actual (days) | 11.8 | 11.7 | 12.3 | 8.0 |
| Reviews | 99,224 | 98,899 | 42,735 | 4,786 |
| Avg review | 4.09 | 4.09 | 4.11 | 4.11 |
| % negative | 14.7% | 14.6% | 13.9% | 13.4% |
| Avg review - late delivery | 2.27 | 2.27 | 2.35 | 2.63 |
| Avg review - on time | 4.29 | 4.29 | 4.29 | 4.27 |
| Payment value | 16,008,872.12 | 15,944,480.57 | 7,249,746.73 | 1,194,882.80 |
| Payments | 103,886 | 103,520 | 47,525 | 7,863 |
| Avg installments | 2.85 | 2.85 | 3.00 | 3.02 |
| Customers | 96,096 | 95,774 | 43,713 | 7,430 |
| Repeat customers | 2,997 | 2,975 | 1,256 | 109 |
| Repeat customer rate | 3.12% | 3.11% | 2.87% | 1.47% |

## 10. Checklist dựng (đánh dấu khi xong)

- [ ] **Đa dạng biểu đồ (≥ 4 loại)**: Bar chart, Card, Clustered column, Column, Donut, Funnel, Map hoặc bar chart, Matrix, Stacked column, Table
- [ ] **Định dạng số**: xem bảng định dạng bên dưới
- [ ] **Tiêu đề dạng câu hỏi**: xem danh sách tiêu đề bên dưới
- [ ] **Màu đỏ chỉ để cảnh báo**: mục 6: đỏ chỉ ở định dạng có điều kiện (trễ, hủy, điểm review thấp)
- [ ] **Định dạng có điều kiện**: Card On-time rate, Cancel rate, Avg review; bản đồ Late rate; cohort color scale
- [ ] **Slicer phân cấp**: slicer Năm → Quý → Tháng và Vùng → Bang
- [ ] **OLAP drill-down / roll-up**: bản đồ / bảng Geography Vùng → Bang → Thành phố; cohort năm → tháng
- [ ] **Tooltip**: `Tooltip_Muc_tre` và tooltip theo bang
- [ ] **Thống kê: Key Influencers**: trang 3: visual Key influencers cho `Review type` = Tiêu cực
- [ ] **Publish web và mã QR**: cùng báo cáo với các dashboard khác
- [ ] **Số liệu khớp bảng giá trị kỳ vọng ở mục 9**: đối chiếu từng card
- [ ] **Màu theo `powerbi/theme.json`; font Segoe UI; không quá 6–8 visual một trang**
- [ ] **Ảnh chụp**: đặt tên `4_DB2_<mô-tả>.png` (ví dụ `4_DB2_trang1_tong_quan.png`) vào `figures/`
