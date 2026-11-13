# DB4 – Thu hút và hiệu quả seller

*Loại: Vận hành (funnel). Người dựng: Người 4 (Phú dựng file gốc, tổng hợp và chỉnh sửa). Dựng theo `powerbi/model.md` (mục 8); công thức DAX ở `powerbi/measures.md`. Cây phân tích: `huong-dan/05-nghiep-vu-nhap.md` mục 6 (hình `figures/2-3_cay_phan_tich_DB4.png`).*

## 1. Mục tiêu

Đo hiệu quả thu hút seller (2 trang): kênh nào chuyển đổi tốt, chốt deal mất bao lâu, seller từ funnel có bán được không (luôn ghi cỡ mẫu); trang thứ ba là trang drill-through chi tiết từng seller.

## 2. Câu hỏi trả lời, người dùng và tần suất xem

- Bao nhiêu % MQL được chốt, theo kênh?
- Chốt deal và có đơn đầu tiên mất bao lâu?
- Seller từ funnel đóng góp GMV bao nhiêu, giao trễ và review ra sao?
- Seller nào GMV cao nhưng hay trễ?

| Người dùng | Câu hỏi | Tần suất xem |
| --- | --- | --- |
| Quản lý seller và đội sales (SDR, SR) | Kênh nào chuyển đổi tốt; seller từ funnel bán ra sao? | hằng tuần, hằng tháng |

## 3. Bố cục từng trang

Trang 16:9 chia 12 cột; số hàng là thứ tự từ trên xuống. Mỗi dòng là một visual. Bộ lọc trang `dim_date[InWindow] = TRUE` (2017-01 → 2018-08).

### Trang 1 – Funnel theo kênh

| Hàng | Cột (trong 12) | Visual | Trường / measure |
| --- | --- | --- | --- |
| 1 | 1–5 | Funnel | `MQLs` → `Won deals` → `Sellers with first sale` |
| 1 | 6–12 | Bar chart | `MQL to won rate` theo `dim_lead_origin[origin]` (kèm `MQLs` ở tooltip) |
| 1 | 1–4 | Card | Won to first sale rate; Avg days won to first sale; Seller GMV first 90d |
| 1 | 5–8 | Column | `Avg days to close` theo `dim_lead_origin[channel_group]` |
| 1 | 9–12 | Line chart | `MQLs` theo `year_month` (tháng liên hệ đầu), tách theo `channel_group` |

### Trang 2 – Seller từ funnel và hiệu suất

| Hàng | Cột (trong 12) | Visual | Trường / measure |
| --- | --- | --- | --- |
| 2 | 1–6 | Table | `v_seller_scorecard` lọc `is_from_funnel = TRUE`: `seller_id`, `acquisition_channel`, `orders`, `gmv`, `late_rate_pct`, `avg_review_score`, `small_sample` |
| 2 | 7–12 | Column + chữ | `v_seller_by_channel`: `acquisition_channel` → `gmv_per_selling_seller`; `selling_sellers` và `small_sample` hiện kèm |
| 2 | 1–6 | Scatter | `v_seller_scorecard`: x `gmv`, y `late_rate_pct`, kích thước `orders` (seller GMV cao nhưng hay trễ) |
| 2 | 7–12 | Card | Won deals − Sellers with first sale = deal chốt nhưng chưa bán (462) |

### Trang 3 – Chi tiết seller (drill-through)

| Hàng | Cột (trong 12) | Visual | Trường / measure |
| --- | --- | --- | --- |
| 1 | 1–12 | Card ×5 | `dim_seller[seller_id]`, `[acquisition_channel]`, `[state_code]`; `Seller GMV (monthly)`; `Seller late rate` |
| 2 | 1–8 | Line chart | `Seller GMV (monthly)` theo `dim_date[year_month]` (thấy tháng seller ngừng bán nhờ snapshot dày đặc) |
| 2 | 9–12 | Table | tháng, số đơn, số đơn trễ của seller (`fact_seller_monthly`) |
| 3 | 1–11 | Card | `Small sample warning` |
| 3 | 12 | Button | nút Back |

### Trang tooltip `Tooltip_Kenh`

| Hàng | Cột (trong 12) | Visual | Trường / measure |
| --- | --- | --- | --- |
| 1 | 1–12 | Card ×4 | `MQLs`, `Won deals`, `MQL to won rate`, cỡ mẫu theo kênh đang trỏ |

## 4. Visual, measure, slicer

**KPI và measure dùng**

| Measure | Ý nghĩa |
| --- | --- |
| **MQLs** | số khách tiềm năng |
| **Won deals** | đã chốt |
| **MQL to won rate** | tỷ lệ chốt |
| **Avg days to close** | ngày liên hệ → chốt |
| **Sellers with first sale** | seller đã có đơn |
| **Won to first sale rate** | đã chốt → có đơn |
| **Avg days won to first sale** | chốt → đơn đầu |
| **Seller GMV first 90d** | GMV 90 ngày đầu |
| **Small sample warning** | cảnh báo mẫu nhỏ |

Mã DAX đầy đủ từng measure: `powerbi/measures.md`. Màu cảnh báo: các measure `Color …` ở mục 6 của file đó.

**Slicer và bộ lọc**

- `dim_lead_origin[channel_group]`
- `dim_lead_profile[business_segment]`
- `v_seller_scorecard[acquisition_channel]`, `[state_code]` (trang 2)
- Slicer kênh dạng phân cấp `dim_lead_origin` Nhóm kênh → Origin
- Bộ lọc trang `dim_date[InWindow] = TRUE` (2017-01 → 2018-08).

## 5. Drill-down, drill-through, tooltip

- Origin → kênh (hierarchy Lead origin)
- Bảng seller: drill-through sang `fact_seller_monthly` của seller (đường GMV theo tháng)
- Drill-through: trang *Chi tiết seller* có trường drill-through `dim_seller[seller_id]`; ở trang 2, bảng `dim_seller[seller_id]` + `Seller GMV (monthly)` + `Seller late rate` có quan hệ với `fact_seller_monthly` nên chuột phải một seller → *Drill through* lọc đúng (bảng `v_seller_scorecard` là bảng rời, chỉ dùng để hiển thị điểm review).
- Tooltip: gán `Tooltip_Kenh` cho thanh `MQL to won rate` theo origin.

## 6. Định dạng có điều kiện và DAX đặc biệt

- Cột `late_rate_pct`: đỏ nếu > 10%
- `small_sample = TRUE`: chữ xám và dòng cảnh báo `Small sample warning`
- Cột `avg_review_score`: xanh/vàng/đỏ theo `Color Avg review`

**Cảnh báo mẫu nhỏ**

```dax
Small sample warning = IF ( [Active sellers] < 30, "⚠ Mẫu nhỏ (dưới 30 seller)", "" )
```

**Role-playing date: deal theo ngày chốt**

```dax
Won deals by won date = CALCULATE ( [Won deals], USERELATIONSHIP ( fact_lead_funnel[won_date_key], dim_date[date_key] ) )
```

## 7. Đáp ứng checklist

Checklist chung ở [`README.md`](README.md); ma trận mục × dashboard ở đó.

| Mục checklist | Đáp ứng | Cách đáp ứng trong DB4 |
| --- | --- | --- |
| Định dạng số | ✓ | xem bảng định dạng bên dưới |
| Tiêu đề dạng câu hỏi | ✓ | xem danh sách tiêu đề bên dưới |
| Màu đỏ chỉ để cảnh báo | ✓ | mục 6: đỏ chỉ ở `late_rate_pct` > 10% và cảnh báo mẫu nhỏ |
| Định dạng có điều kiện | ✓ | `late_rate_pct`, `small_sample`, `avg_review_score` theo `Color …` |
| Slicer phân cấp | ✓ | slicer Nhóm kênh → Origin |
| OLAP drill-down / roll-up | ✓ | drill Origin → Nhóm kênh; bảng seller drill theo bang |
| Drill-through | ✓ | trang *Chi tiết seller* (trường `seller_id`) |
| Tooltip | ✓ | `Tooltip_Kenh` |
| Chuỗi thời gian có dự báo | – | không áp dụng (dự báo ở DB1) |
| Thống kê: Key Influencers | – | không áp dụng (Key Influencers ở DB2) |
| Publish web và mã QR | ✓ | cùng báo cáo với các dashboard khác |

**Định dạng số** (*Measure tools → Format → Custom* hoặc *Display units* của visual):

| Chỉ số | Loại | Định dạng |
| --- | --- | --- |
| MQLs, Won deals | số | `#,0` |
| MQL to won rate, Won to first sale rate, Seller late rate | phần trăm | `0.0%` |
| Avg days to close, Avg days won to first sale | ngày | `0.0` |
| Seller GMV (monthly), Seller GMV first 90d | tiền | `#,0.0,"K"` |

**Tiêu đề visual dạng câu hỏi** (lấy từ mục 2; mỗi visual chọn một câu phù hợp làm tiêu đề):

- Bao nhiêu % MQL được chốt, theo kênh?
- Chốt deal và có đơn đầu tiên mất bao lâu?
- Seller từ funnel đóng góp GMV bao nhiêu, giao trễ và review ra sao?
- Seller nào GMV cao nhưng hay trễ?

## 8. Insight gợi ý (có số thật, để viết vào báo cáo và slide)

1. **8.000 MQL → 842 deal (10,5%) → 379 seller có đơn bán được (45,0% số đã chốt, tức 4,74% MQL)**; 462 deal chốt nhưng chưa bán.
2. Tỷ lệ chốt theo origin: `unknown` 16,7%, `paid_search` 12,3%, `organic_search` 11,8%… thấp nhất `email` 3,0% (493 MQL) và `other` 2,7% (150 MQL).
3. Thời gian chốt TB 48,5 ngày (Social 61,0; Paid 55,0; Organic 45,9; Unknown 41,9); từ chốt đến đơn đầu TB 51,9 ngày.
4. Seller từ funnel chỉ tạo ~5% GMV: kênh Organic 153 seller có đơn (GMV 246.767), Unknown 85 (214.726), Paid 103 (153.720), Social 31, Email 6 (**mẫu nhỏ**), Other 2 (**mẫu nhỏ**).
5. Seller Unknown có **GMV/seller cao nhất (2.526 BRL)** trong các nhóm funnel nhưng mẫu 85 seller; Organic chỉ 1.613 BRL/seller – cần nói rõ cỡ mẫu khi so sánh.

Trang 2 dùng bảng mart (toàn bộ giai đoạn, không lọc ngày): ghi rõ trên tiêu đề.

## 9. Bảng giá trị kỳ vọng (SQL trên trạng thái cuối, để đối chiếu số trên Power BI)

Cột **Cửa sổ 2017-01 → 2018-08** là số khi bật bộ lọc trang `InWindow`; cột **Toàn bộ dữ liệu** khi bỏ lọc. Sinh bởi `python scripts/gen_powerbi_docs.py` rồi chạy lại `python scripts/gen_dashboard_docs.py`.

| Measure | Toàn bộ dữ liệu | Cửa sổ 2017-01 → 2018-08 | Năm 2017 | Tháng 2017-11 |
| --- | ---: | ---: | ---: | ---: |
| MQLs (theo tháng liên hệ đầu) | 8,000 | 8,000 | 2,002 | 445 |
| Won deals | 842 | 842 | 61 | 18 |
| MQL to won rate | 10.5% | 10.5% | 3.0% | 4.0% |
| Avg days to close | 48.5 | 48.5 | 212.2 | 155.1 |
| Sellers with first sale | 379 | 379 | 19 | 6 |
| Won to first sale rate | 45.0% | 45.0% | 31.1% | 33.3% |
| Avg days won to first sale | 51.9 | 51.9 | 42.9 | 42.8 |
| Seller GMV first 90d | 538,271.72 | 538,271.72 | 19,413.78 | 2,085.32 |
| Active sellers (fact_seller_monthly) | 3,095 | 3,068 | 1,784 | 965 |
| Seller GMV (monthly) | 13,494,400.74 | 13,449,529.68 | 6,108,492.27 | 1,003,862.14 |
| Seller late rate | 6.7% | 6.7% | 5.6% | 12.3% |

## 10. Checklist dựng (đánh dấu khi xong)

- [ ] **Đa dạng biểu đồ (≥ 4 loại)**: Bar chart, Card, Column, Column + chữ, Funnel, Line chart, Scatter, Table
- [ ] **Định dạng số**: xem bảng định dạng bên dưới
- [ ] **Tiêu đề dạng câu hỏi**: xem danh sách tiêu đề bên dưới
- [ ] **Màu đỏ chỉ để cảnh báo**: mục 6: đỏ chỉ ở `late_rate_pct` > 10% và cảnh báo mẫu nhỏ
- [ ] **Định dạng có điều kiện**: `late_rate_pct`, `small_sample`, `avg_review_score` theo `Color …`
- [ ] **Slicer phân cấp**: slicer Nhóm kênh → Origin
- [ ] **OLAP drill-down / roll-up**: drill Origin → Nhóm kênh; bảng seller drill theo bang
- [ ] **Drill-through**: trang *Chi tiết seller* (trường `seller_id`)
- [ ] **Tooltip**: `Tooltip_Kenh`
- [ ] **Publish web và mã QR**: cùng báo cáo với các dashboard khác
- [ ] **Số liệu khớp bảng giá trị kỳ vọng ở mục 9**: đối chiếu từng card
- [ ] **Màu theo `powerbi/theme.json`; font Segoe UI; không quá 6–8 visual một trang**
- [ ] **Ảnh chụp**: đặt tên `4_DB4_<mô-tả>.png` (ví dụ `4_DB4_trang1_tong_quan.png`) vào `figures/`
