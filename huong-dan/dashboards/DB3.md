# DB3 – Địa lý và phí vận chuyển

*Loại: OLAP. Người dựng: Người 3 (Phú dựng file gốc, tổng hợp và chỉnh sửa). Dựng theo `powerbi/model.md` (mục 8); công thức DAX ở `powerbi/measures.md`. Cây phân tích: `huong-dan/05-nghiep-vu-nhap.md` mục 6 (hình `figures/2-3_cay_phan_tich_DB3.png`).*

## 1. Mục tiêu

Cho thấy doanh số và phí vận chuyển phân bố theo địa lý với drill-down Vùng → Bang → Thành phố, và quan hệ giữa khoảng cách, phí vận chuyển và thời gian giao; có trang drill-through chi tiết từng bang và tooltip.

## 2. Câu hỏi trả lời, người dùng và tần suất xem

- GMV tập trung ở vùng / bang nào?
- Phí vận chuyển chiếm bao nhiêu % giá hàng theo vùng?
- Seller và khách xa nhau bao nhiêu và điều đó ảnh hưởng freight và lead time ra sao?

| Người dùng | Câu hỏi | Tần suất xem |
| --- | --- | --- |
| Quản lý vận hành và logistics | Phí vận chuyển chiếm bao nhiêu % giá hàng theo vùng; bang nào giao chậm? | hằng ngày đến hằng tuần |
| Quản lý kinh doanh | GMV tập trung ở vùng, bang nào? | hằng tháng |

## 3. Bố cục từng trang

Trang 16:9 chia 12 cột; số hàng là thứ tự từ trên xuống. Mỗi dòng là một visual. Bộ lọc trang `dim_date[InWindow] = TRUE` (2017-01 → 2018-08).

### Trang 1 – Địa lý và phí vận chuyển

| Hàng | Cột (trong 12) | Visual | Trường / measure |
| --- | --- | --- | --- |
| 1 | 1–4 | Card | GMV; Freight ratio |
| 1 | 5–8 | Card | Avg lead days |
| 1 | 9–12 | Card | Số bang / zip có đơn (đếm `dim_geography[state_code]`) |
| 2 | 1–7 | Map (bản đồ bong bóng) | vị trí `latitude`/`longitude` của `dim_geography` (hoặc bảng `v_geo_state`); kích thước `GMV`; màu `Freight ratio` |
| 2 | 8–12 | Bar chart | `Freight ratio` theo `state_code` (top 10), màu theo `Color Freight ratio` |
| 3 | 1–6 | Matrix | hierarchy Geography (vùng → bang → thành phố); giá trị `GMV`, `Freight`, `Freight ratio`, `Avg lead days` |
| 3 | 7–12 | Clustered column | `GMV` (địa lý khách) cạnh `GMV by seller state` (địa lý seller) theo `region` |

### Trang 2 – Chi tiết bang (drill-through)

| Hàng | Cột (trong 12) | Visual | Trường / measure |
| --- | --- | --- | --- |
| 1 | 1–12 | Card ×5 | `GMV`, `Orders`, `Freight ratio`, `Avg lead days`, `Late rate` của bang đang chọn |
| 2 | 1–6 | Table | `dim_geography[city]` → `GMV`, `Freight ratio`, `Avg lead days` (thành phố của bang) |
| 2 | 7–12 | Clustered column | `GMV` theo `dim_date[year_month]` của bang |
| 3 | 1–12 | Line chart | `Avg lead days` theo `dim_date[year_month]` của bang |
| 3 | 12 | Button | nút Back (*Insert → Buttons → Back*) |

### Trang tooltip `Tooltip_Bang`

| Hàng | Cột (trong 12) | Visual | Trường / measure |
| --- | --- | --- | --- |
| 1 | 1–12 | Card ×4 | `GMV`, `Freight ratio`, `Avg lead days`, `Late rate` theo bang đang trỏ |

## 4. Visual, measure, slicer

**KPI và measure dùng**

| Measure | Ý nghĩa |
| --- | --- |
| **GMV** | doanh thu |
| **Freight** | phí vận chuyển |
| **Freight ratio** | freight / giá hàng |
| **Avg lead days** | thời gian giao TB |
| **GMV by seller state** | GMV theo địa lý seller (role-playing) |

Mã DAX đầy đủ từng measure: `powerbi/measures.md`. Màu cảnh báo: các measure `Color …` ở mục 6 của file đó.

**Slicer và bộ lọc**

- `dim_date[year]`
- `dim_product[category_group]`
- `dim_product[size_class]`
- `dim_geography[region]`
- Slicer địa lý dạng phân cấp `dim_geography` Vùng → Bang
- Bộ lọc trang `dim_date[InWindow] = TRUE` (2017-01 → 2018-08).

## 5. Drill-down, drill-through, tooltip

- Hierarchy Geography: Vùng → Bang → Thành phố → Zip
- Bản đồ: drill từ bang xuống thành phố
- Drill-through: trang *Chi tiết bang* có trường drill-through `dim_geography[state_code]` (*Keep all filters*); chuột phải một bang ở bản đồ, thanh hoặc ma trận → *Drill through* → *Chi tiết bang*.
- Tooltip: gán `Tooltip_Bang` cho bản đồ và thanh `Freight ratio` theo bang.

## 6. Định dạng có điều kiện và DAX đặc biệt

- Matrix: data bars trên `GMV`; màu `Freight ratio` theo `Color Freight ratio`
- Bản đồ: màu bong bóng theo `Freight ratio`

**Địa lý seller bằng USERELATIONSHIP**

```dax
GMV by seller state =
CALCULATE ( [GMV], USERELATIONSHIP ( fact_order_item[seller_geography_key], dim_geography[geography_key] ) )
```

## 7. Đáp ứng checklist

Checklist chung ở [`README.md`](README.md); ma trận mục × dashboard ở đó.

| Mục checklist | Đáp ứng | Cách đáp ứng trong DB3 |
| --- | --- | --- |
| Định dạng số | ✓ | xem bảng định dạng bên dưới |
| Tiêu đề dạng câu hỏi | ✓ | xem danh sách tiêu đề bên dưới |
| Màu đỏ chỉ để cảnh báo | ✓ | mục 6: đỏ chỉ ở màu `Freight ratio` cao |
| Định dạng có điều kiện | ✓ | matrix data bars, màu `Freight ratio`; bản đồ màu bong bóng |
| Slicer phân cấp | ✓ | slicer Vùng → Bang |
| OLAP drill-down / roll-up | ✓ | **OLAP chính**: Vùng → Bang → Thành phố → Zip trên bản đồ và ma trận, drill-down và roll-up |
| Drill-through | ✓ | trang *Chi tiết bang* (trường `state_code`) |
| Tooltip | ✓ | `Tooltip_Bang` |
| Chuỗi thời gian có dự báo | – | không áp dụng (dự báo ở DB1) |
| Thống kê: Key Influencers | – | không áp dụng (Key Influencers ở DB2) |
| Publish web và mã QR | ✓ | cùng báo cáo với các dashboard khác |

**Định dạng số** (*Measure tools → Format → Custom* hoặc *Display units* của visual):

| Chỉ số | Loại | Định dạng |
| --- | --- | --- |
| GMV theo bang | tiền | `#,0.0,"K"` hoặc `#,0.0,,"M"` |
| Freight ratio, Late rate | phần trăm | `0.0%` |
| Avg lead days | ngày | `0.0` |
| Khoảng cách | km | `#,0` |

**Tiêu đề visual dạng câu hỏi** (lấy từ mục 2; mỗi visual chọn một câu phù hợp làm tiêu đề):

- GMV tập trung ở vùng / bang nào?
- Phí vận chuyển chiếm bao nhiêu % giá hàng theo vùng?
- Seller và khách xa nhau bao nhiêu và điều đó ảnh hưởng freight và lead time ra sao?

## 8. Insight gợi ý (có số thật, để viết vào báo cáo và slide)

1. **Sudeste 65,4% GMV, Sul 14,4%, Nordeste 11,4%, Centro-Oeste 6,4%, Norte 2,5%.**
2. Phí vận chuyển nặng ở vùng xa: **Norte 22,7% và Nordeste 21,7% giá hàng so với 15,2% ở Sudeste**.
3. Từ dưới 100 km lên trên 1.000 km, phí vận chuyển TB tăng 11,75 → 31,65 BRL và lead time 6,5 → 19,0 ngày (xem `handoff/geo-distance.md`).
4. Seller và khách **cùng bang ở 36,1%** dòng hàng; khoảng cách TB 598 km (trung vị 433 km).
5. 555 dòng hàng (0,49%) không tính được khoảng cách vì thiếu toạ độ; cần ghi chú trên trang.

Mart hỗ trợ: `v_geo_state` (27 bang), `v_geo_zip` (14.889 zip), `v_shipping_distance` (khoảng cách từng dòng hàng, không xuất CSV).

## 9. Bảng giá trị kỳ vọng (SQL trên trạng thái cuối, để đối chiếu số trên Power BI)

Cột **Cửa sổ 2017-01 → 2018-08** là số khi bật bộ lọc trang `InWindow`; cột **Toàn bộ dữ liệu** khi bỏ lọc. Sinh bởi `python scripts/gen_powerbi_docs.py` rồi chạy lại `python scripts/gen_dashboard_docs.py`.

| Measure | Toàn bộ dữ liệu | Cửa sổ 2017-01 → 2018-08 | Năm 2017 | Tháng 2017-11 |
| --- | ---: | ---: | ---: | ---: |
| GMV | 13,494,400.74 | 13,449,529.68 | 6,108,492.27 | 1,003,862.14 |
| Orders | 98,199 | 97,905 | 44,375 | 7,421 |
| Freight | 2,241,126.29 | 2,234,177.06 | 982,076.97 | 168,329.54 |
| Freight ratio | 16.6% | 16.6% | 16.1% | 16.8% |
| Avg lead days | 12.6 | 12.5 | 13.0 | 15.2 |
| Late rate | 6.8% | 6.8% | 5.6% | 12.4% |

## 10. Checklist dựng (đánh dấu khi xong)

- [ ] **Đa dạng biểu đồ (≥ 4 loại)**: Bar chart, Card, Clustered column, Map, Matrix
- [ ] **Định dạng số**: xem bảng định dạng bên dưới
- [ ] **Tiêu đề dạng câu hỏi**: xem danh sách tiêu đề bên dưới
- [ ] **Màu đỏ chỉ để cảnh báo**: mục 6: đỏ chỉ ở màu `Freight ratio` cao
- [ ] **Định dạng có điều kiện**: matrix data bars, màu `Freight ratio`; bản đồ màu bong bóng
- [ ] **Slicer phân cấp**: slicer Vùng → Bang
- [ ] **OLAP drill-down / roll-up**: **OLAP chính**: Vùng → Bang → Thành phố → Zip trên bản đồ và ma trận, drill-down và roll-up
- [ ] **Drill-through**: trang *Chi tiết bang* (trường `state_code`)
- [ ] **Tooltip**: `Tooltip_Bang`
- [ ] **Publish web và mã QR**: cùng báo cáo với các dashboard khác
- [ ] **Số liệu khớp bảng giá trị kỳ vọng ở mục 9**: đối chiếu từng card
- [ ] **Màu theo `powerbi/theme.json`; font Segoe UI; không quá 6–8 visual một trang**
- [ ] **Ảnh chụp**: đặt tên `4_DB3_<mô-tả>.png` (ví dụ `4_DB3_trang1_tong_quan.png`) vào `figures/`
