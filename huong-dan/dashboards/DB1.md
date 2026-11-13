# DB1 – Tổng quan và doanh thu

*Loại: Theo dòng thời gian, có dự báo. Người dựng: Người 1 (Phú dựng file gốc, tổng hợp và chỉnh sửa). Dựng theo `powerbi/model.md` (mục 8); công thức DAX ở `powerbi/measures.md`. Cây phân tích: `huong-dan/05-nghiep-vu-nhap.md` mục 6 (hình `figures/2-3_cay_phan_tich_DB1.png`).*

## 1. Mục tiêu

Cho thấy sức khoẻ doanh thu của sàn trong một dashboard: doanh thu, giao hàng, hài lòng và xu hướng theo tháng (kèm dự báo), rồi đào sâu doanh số theo sản phẩm: ngành hàng nào bán chạy, quy luật 80/20, giá và phí vận chuyển theo ngành.

## 2. Câu hỏi trả lời, người dùng và tần suất xem

- Doanh thu (GMV) bao nhiêu, tăng hay giảm so với tháng trước và cùng kỳ năm trước?
- Giao hàng có đúng hạn không, tỷ lệ hủy bao nhiêu?
- Khách hài lòng không (điểm review)?
- Vùng nào và nhóm ngành nào đóng góp nhiều nhất?
- Nhóm ngành / danh mục nào tạo nhiều GMV nhất và thay đổi thế nào theo quý?
- Bao nhiêu danh mục tạo 80% GMV (Pareto)?
- AOV và phí vận chuyển của từng ngành ra sao?

| Người dùng | Câu hỏi | Tần suất xem |
| --- | --- | --- |
| Ban điều hành | Doanh thu có tăng không? Giao hàng và khách hàng ra sao? | hằng tuần, hằng tháng |
| Quản lý kinh doanh và danh mục | Nhóm ngành nào bán chạy; giá và phí vận chuyển theo ngành? | hằng tuần |

## 3. Bố cục từng trang

Trang 16:9 chia 12 cột; số hàng là thứ tự từ trên xuống. Mỗi dòng là một visual. Bộ lọc trang `dim_date[InWindow] = TRUE` (2017-01 → 2018-08).

### Trang 1 – Tổng quan

| Hàng | Cột (trong 12) | Visual | Trường / measure |
| --- | --- | --- | --- |
| 1 | 1–2 | Card | GMV (+ `GMV MoM %` làm chú thích, màu `Color growth`) |
| 1 | 3–4 | Card | Orders |
| 1 | 5–6 | Card | AOV |
| 1 | 7–8 | Card | On-time rate (màu `Color On-time rate`) |
| 1 | 9–10 | Card | Avg review (màu `Color Avg review`) |
| 1 | 11–12 | Card | Cancel rate (màu `Color Cancel rate`) |
| 2 | 1–8 | Line chart (đường) | trục `dim_date[year_month]`; giá trị `GMV` và `GMV last year` |
| 2 | 9–12 | Clustered column (cột) | `GMV MoM %` theo tháng, màu theo `Color growth` |
| 3 | 1–4 | Bar chart ngang | `GMV` theo `dim_geography[region]` |
| 3 | 5–8 | Treemap | `GMV` theo `dim_product[category_group]` |
| 3 | 9–12 | Gauge hoặc KPI visual | `On-time rate` với mục tiêu 95% |

### Trang 2 – Doanh thu theo sản phẩm

| Hàng | Cột (trong 12) | Visual | Trường / measure |
| --- | --- | --- | --- |
| 1 | 1–3 | Card | GMV |
| 1 | 4–6 | Card | Items |
| 1 | 7–9 | Card | AOV |
| 1 | 10–12 | Card | Freight ratio |
| 2 | 1–5 | Treemap | `dim_product[category_group]` → `GMV` |
| 2 | 6–12 | Combo cột + đường (Pareto) | bảng `v_category_pareto`: trục `category_name_en` (sắp theo `gmv_rank`), cột `gmv`, đường `cum_share_pct`; màu theo `abc_class` |
| 3 | 1–7 | Matrix | hàng: hierarchy Product; cột `dim_date[year_quarter]`; giá trị `GMV`, `Items`, `AOV` |
| 3 | 8–12 | Scatter | x `AOV`, y `Freight ratio`, chi tiết `category_group`, kích thước `GMV` |

### Trang tooltip `Tooltip_Thang`

| Hàng | Cột (trong 12) | Visual | Trường / measure |
| --- | --- | --- | --- |
| 1 | 1–12 | Card ×4 | `GMV`, `Orders`, `AOV`, `On-time rate` theo tháng đang trỏ (*Page size = Tooltip*, *Allow use as tooltip = On*) |

## 4. Visual, measure, slicer

**KPI và measure dùng**

| Measure | Ý nghĩa |
| --- | --- |
| **GMV** | doanh thu hàng bán (không tính đơn Failed) |
| **Orders** | số đơn có doanh thu |
| **AOV** | giá trị TB mỗi đơn |
| **On-time rate** | tỷ lệ giao đúng hạn |
| **Avg review** | điểm review TB |
| **Cancel rate** | tỷ lệ hủy |
| **GMV MoM %** | tăng trưởng so với tháng trước |
| **GMV YoY %** | tăng trưởng so với cùng kỳ năm trước |
| **GMV last year** | đường so sánh cùng kỳ |
| **Items** | số dòng hàng đã bán |
| **Freight ratio** | phí vận chuyển / giá hàng |
| **Avg items per order** | số dòng hàng TB mỗi đơn |

Mã DAX đầy đủ từng measure: `powerbi/measures.md`. Màu cảnh báo: các measure `Color …` ở mục 6 của file đó.

**Slicer và bộ lọc**

- `dim_date[year]` (dạng nút)
- `dim_geography[region]` (danh sách)
- `dim_order_status[status_group]` (mặc định bỏ chọn; GMV vốn đã loại Failed)
- `dim_date[year_quarter]`
- `dim_product[category_group]`
- `dim_product[size_class]`
- `dim_geography[state_code]`
- Slicer thời gian dạng phân cấp: `dim_date` Năm → Quý → Tháng (trang 1 dùng `year`, trang 2 dùng `year_quarter`)
- Bộ lọc trang `dim_date[InWindow] = TRUE` (2017-01 → 2018-08).

## 5. Drill-down, drill-through, tooltip

- Line chart: Date hierarchy Năm → Quý → Tháng (mũi tên drill-down)
- Treemap: nhóm ngành → danh mục (`Product` hierarchy)
- Matrix và treemap: hierarchy Product (nhóm ngành → danh mục → sản phẩm)
- Matrix: mở cột Quý → Tháng
- Chuỗi thời gian có dự báo: line chart `GMV` theo `dim_date[year_month]` → ngăn *Analytics* → *Forecast* → *Forecast length = 3 điểm*, *Confidence interval = 95%*. Dữ liệu chỉ có 20 tháng nên dự báo chỉ để thấy hướng đi; ghi chú cạnh biểu đồ (xem báo cáo mục 3.1: chưa đủ cơ sở kết luận mùa vụ theo năm).
- Tooltip: gán `Tooltip_Thang` cho đường GMV và cột `GMV MoM %`; gán một tooltip theo nhóm ngành cho treemap (GMV, Items, AOV, Freight ratio).

## 6. Định dạng có điều kiện và DAX đặc biệt

- Cards On-time rate / Avg review / Cancel rate: **Field value** theo `Color …` (xanh / vàng / đỏ)
- Cột `GMV MoM %`: xanh nếu dương, đỏ nếu âm (`Color growth`)
- Matrix: **color scale** (nền) trên `GMV`
- Pareto: cột tô theo hạng A/B/C (A xanh, B vàng, C xám)
- Scatter: điểm có `Freight ratio` > 25% màu đỏ (`Color Freight ratio`)

**Tăng trưởng và cảnh báo**

```dax
GMV last month = CALCULATE ( [GMV], DATEADD ( dim_date[full_date], -1, MONTH ) )
GMV MoM % = DIVIDE ( [GMV] - [GMV last month], [GMV last month] )
Alert text = (xem powerbi/measures.md mục 9)
```

**Tỷ trọng và luỹ kế (nếu không dùng bảng mart)**

```dax
GMV share = DIVIDE ( [GMV], CALCULATE ( [GMV], ALL ( dim_product ) ) )
Avg items per order = DIVIDE ( [Items], [Orders] )
```

## 7. Đáp ứng checklist

Checklist chung ở [`README.md`](README.md); ma trận mục × dashboard ở đó.

| Mục checklist | Đáp ứng | Cách đáp ứng trong DB1 |
| --- | --- | --- |
| Định dạng số | ✓ | xem bảng định dạng bên dưới |
| Tiêu đề dạng câu hỏi | ✓ | xem danh sách tiêu đề bên dưới |
| Màu đỏ chỉ để cảnh báo | ✓ | mục 6: đỏ chỉ ở định dạng có điều kiện (cột `GMV MoM %` âm, `Freight ratio` > 25%) |
| Định dạng có điều kiện | ✓ | Card On-time rate, Avg review, Cancel rate; cột tăng trưởng; matrix color scale |
| Slicer phân cấp | ✓ | slicer Năm → Quý → Tháng |
| OLAP drill-down / roll-up | ✓ | line chart Năm → Quý → Tháng; treemap và matrix Nhóm ngành → Danh mục → Sản phẩm |
| Drill-through | – | không áp dụng (drill-through nằm ở DB3, DB4) |
| Tooltip | ✓ | `Tooltip_Thang` và tooltip theo nhóm ngành |
| Chuỗi thời gian có dự báo | ✓ | line chart GMV theo tháng có *Forecast* 3 điểm, tin cậy 95% |
| Thống kê: Key Influencers | – | không áp dụng (Key Influencers ở DB2) |
| Publish web và mã QR | ✓ | cùng báo cáo với các dashboard khác (`powerbi/model.md` mục 9) |

**Định dạng số** (*Measure tools → Format → Custom* hoặc *Display units* của visual):

| Chỉ số | Loại | Định dạng |
| --- | --- | --- |
| GMV | tiền | `#,0.0,,"M"` → 13.5M |
| Orders, Items | số | `#,0.0,"K"` → 98.2K |
| AOV | tiền | `#,0.0` → 137.4 |
| On-time rate, Cancel rate, Freight ratio | phần trăm | `0.0%` → 93.2% |
| Avg review | điểm | `0.00` → 4.09 |
| GMV MoM %, GMV YoY % | phần trăm | `+0.0%;-0.0%` |

**Tiêu đề visual dạng câu hỏi** (lấy từ mục 2; mỗi visual chọn một câu phù hợp làm tiêu đề):

- Doanh thu (GMV) bao nhiêu, tăng hay giảm so với tháng trước và cùng kỳ năm trước?
- Giao hàng có đúng hạn không, tỷ lệ hủy bao nhiêu?
- Khách hài lòng không (điểm review)?
- Vùng nào và nhóm ngành nào đóng góp nhiều nhất?
- Nhóm ngành / danh mục nào tạo nhiều GMV nhất và thay đổi thế nào theo quý?
- Bao nhiêu danh mục tạo 80% GMV (Pareto)?
- AOV và phí vận chuyển của từng ngành ra sao?

## 8. Insight gợi ý (có số thật, để viết vào báo cáo và slide)

1. GMV tăng từ 120.098 BRL (01/2017) lên **1.003.862 BRL (11/2017)**, tháng cao nhất; **+52,1% so với 10/2017** nhờ Black Friday 24/11/2017 (một ngày 152.654 BRL, gấp 5,2 lần ngày thường trong tháng).
2. Từ 03/2018 GMV đi ngang quanh 0,85–0,99 triệu BRL/tháng, nhưng vẫn **cao hơn cùng kỳ năm trước**: 05/2018 +97,3%, 08/2018 +49,4%.
3. **Vùng Sudeste chiếm 65,4% GMV** (8,79 / 13,45 triệu BRL trong cửa sổ), Norte chỉ 2,5%: thị trường tập trung rất mạnh.
4. Giao đúng hạn 93,2% nhưng **tụt còn 87,6% ở 11/2017** (tháng Black Friday) và 81,0% ở 03/2018: tải cao làm giao chậm.
5. Nhóm ngành hàng dẫn đầu: Home & Furniture 22,8% GMV, tiếp theo Gifts & Others và Electronics & Computers (14,0% mỗi nhóm).
6. **18/74 danh mục (24,3%) tạo 80% GMV**; đứng đầu `health_beauty` (9,31%).
7. Home & Furniture dẫn đầu với 3,07 triệu BRL (22,8% GMV trong cửa sổ).
8. AOV toàn sàn 137,42 BRL; phí vận chuyển chiếm 16,6% giá hàng, nhưng **nặng hơn ở hàng giá thấp** (xem scatter AOV – Freight ratio).
9. Doanh số theo quý tăng rõ: quý 4/2017 là 2,41 triệu BRL so với 0,73 triệu ở quý 1/2017.
10. Quy luật 80/20 ở seller yếu hơn: 540/3.053 seller (17,7%) tạo 80% GMV nhưng 5 seller lớn nhất chỉ chiếm 7,7%.

Chân trang ghi: *GMV không gồm đơn hủy / không khả dụng; số liệu BRL; giai đoạn 2017-01 → 2018-08.*

## 9. Bảng giá trị kỳ vọng (SQL trên trạng thái cuối, để đối chiếu số trên Power BI)

Cột **Cửa sổ 2017-01 → 2018-08** là số khi bật bộ lọc trang `InWindow`; cột **Toàn bộ dữ liệu** khi bỏ lọc. Sinh bởi `python scripts/gen_powerbi_docs.py` rồi chạy lại `python scripts/gen_dashboard_docs.py`.

| Measure | Toàn bộ dữ liệu | Cửa sổ 2017-01 → 2018-08 | Năm 2017 | Tháng 2017-11 |
| --- | ---: | ---: | ---: | ---: |
| GMV | 13,494,400.74 | 13,449,529.68 | 6,108,492.27 | 1,003,862.14 |
| Orders | 98,199 | 97,905 | 44,375 | 7,421 |
| Items | 112,101 | 111,752 | 50,617 | 8,626 |
| AOV | 137.42 | 137.37 | 137.66 | 135.27 |
| Freight | 2,241,126.29 | 2,234,177.06 | 982,076.97 | 168,329.54 |
| Freight ratio | 16.6% | 16.6% | 16.1% | 16.8% |
| Orders placed | 99,441 | 99,092 | 45,101 | 7,544 |
| Cancel rate | 1.24% | 1.19% | 1.60% | 1.60% |
| On-time rate | 93.2% | 93.2% | 94.4% | 87.6% |
| Avg review | 4.09 | 4.09 | 4.11 | 4.11 |

**So sánh theo thời gian (GMV)**

| Tháng đang chọn | GMV | GMV last month | GMV MoM % | GMV last year | GMV YoY % |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2017-11 | 1,003,862.14 | 660,179.62 | +52.1% | 0.00 | (trống) |
| 2018-05 | 992,871.75 | 993,592.98 | -0.1% | 503,159.19 | +97.3% |
| 2018-08 | 848,860.10 | 878,044.27 | -3.3% | 568,245.79 | +49.4% |

## 10. Checklist dựng (đánh dấu khi xong)

- [ ] **Đa dạng biểu đồ (≥ 4 loại)**: Bar chart ngang, Card, Clustered column, Combo cột + đường, Gauge hoặc KPI visual, Line chart, Matrix, Scatter, Treemap
- [ ] **Định dạng số**: xem bảng định dạng bên dưới
- [ ] **Tiêu đề dạng câu hỏi**: xem danh sách tiêu đề bên dưới
- [ ] **Màu đỏ chỉ để cảnh báo**: mục 6: đỏ chỉ ở định dạng có điều kiện (cột `GMV MoM %` âm, `Freight ratio` > 25%)
- [ ] **Định dạng có điều kiện**: Card On-time rate, Avg review, Cancel rate; cột tăng trưởng; matrix color scale
- [ ] **Slicer phân cấp**: slicer Năm → Quý → Tháng
- [ ] **OLAP drill-down / roll-up**: line chart Năm → Quý → Tháng; treemap và matrix Nhóm ngành → Danh mục → Sản phẩm
- [ ] **Tooltip**: `Tooltip_Thang` và tooltip theo nhóm ngành
- [ ] **Chuỗi thời gian có dự báo**: line chart GMV theo tháng có *Forecast* 3 điểm, tin cậy 95%
- [ ] **Publish web và mã QR**: cùng báo cáo với các dashboard khác (`powerbi/model.md` mục 9)
- [ ] **Số liệu khớp bảng giá trị kỳ vọng ở mục 9**: đối chiếu từng card
- [ ] **Màu theo `powerbi/theme.json`; font Segoe UI; không quá 6–8 visual một trang**
- [ ] **Ảnh chụp**: đặt tên `4_DB1_<mô-tả>.png` (ví dụ `4_DB1_trang1_tong_quan.png`) vào `figures/`
