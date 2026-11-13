# Hướng dẫn dựng dashboard: DB1–DB4 và checklist chung

Bộ dashboard Power BI gồm **4 dashboard** (gộp từ 7 dashboard ở bản trước, quyết định ngày 13/11). Mỗi dashboard thuộc một loại mà môn học yêu cầu và do một thành viên dựng; Phú làm file `.pbix` gốc, tổng hợp và chỉnh sửa.

| Dashboard | Loại | Người dựng | Hướng dẫn |
| --- | --- | --- | --- |
| DB1 – Tổng quan và doanh thu | Theo dòng thời gian (có dự báo) | Người 1 | [`DB1.md`](DB1.md) |
| DB2 – Giao hàng và trải nghiệm khách | Vận hành + thống kê (Key Influencers) | Người 2 | [`DB2.md`](DB2.md) |
| DB3 – Địa lý và phí vận chuyển | OLAP; drill-down Vùng → Bang → Thành phố; drill-through; tooltip | Người 3 | [`DB3.md`](DB3.md) |
| DB4 – Thu hút và hiệu quả seller (2 trang + trang chi tiết) | Vận hành; funnel; drill-through sang chi tiết seller | Người 4 | [`DB4.md`](DB4.md) |

- **Giám sát chất lượng dữ liệu và ETL** không còn là dashboard: số liệu được trình bày ở mục 3.3 của báo cáo (bảng kết quả nạp và giám sát).
- **Thị trường Brazil (dữ liệu API)** thuộc chương 5 (P9); trang này chỉ để chỗ.
- **DB1 trên Superset** (chương 5) làm sau; xem `5-1-lakehouse.tex`.

## 1. Checklist chung

| Mục | Yêu cầu | Ví dụ / nơi xem |
| --- | --- | --- |
| Định dạng số | mọi số dùng đơn vị rút gọn và dấu phân cách; phần trăm 1 chữ số thập phân | số đơn 12.3K; tiền 13.5M; 12,4% |
| Tiêu đề dạng câu hỏi | mỗi visual có tiêu đề là câu hỏi mà nó trả lời | "GMV tháng này tăng hay giảm so với tháng trước?" |
| Màu đỏ chỉ để cảnh báo | đỏ chỉ ở giá trị xấu hoặc vượt ngưỡng; màu dữ liệu của chủ đề không có đỏ | `powerbi/theme.json` |
| Định dạng có điều kiện | measure DAX trả về màu (`Color …`) cho card, bảng, bản đồ | `powerbi/measures.md` mục 6 |
| Slicer phân cấp | slicer theo phân cấp (Năm → Quý → Tháng; Vùng → Bang; Nhóm kênh → Origin) | hierarchy trong `powerbi/model.md` |
| OLAP drill-down / roll-up | biểu đồ, ma trận, bản đồ có drill-down và drill-up theo phân cấp | DB3: Vùng → Bang → Thành phố → Zip |
| Drill-through | chuột phải một điểm để sang trang chi tiết | DB3: chi tiết bang; DB4: chi tiết seller |
| Tooltip | di chuột hiện trang tooltip | `Tooltip_Thang`, `Tooltip_Muc_tre`, `Tooltip_Bang`, `Tooltip_Kenh` |
| Chuỗi thời gian có dự báo | line chart theo tháng có đường dự báo (Analytics → Forecast) | DB1: GMV theo tháng |
| Thống kê: Key Influencers | visual AI cho biết yếu tố nào đi kèm kết quả cần giải thích | DB2: review tiêu cực |
| Publish web và mã QR | publish công khai (không cần đăng nhập) và mã QR của link | `powerbi/model.md` mục 9 |

## 2. Ma trận đáp ứng (mục checklist × dashboard)

Ký hiệu: **✓** dashboard đáp ứng mục đó; **–** không áp dụng (đã có dashboard khác đáp ứng).

| Mục checklist | DB1 | DB2 | DB3 | DB4 |
| --- | --- | --- | --- | --- |
| Định dạng số | ✓ | ✓ | ✓ | ✓ |
| Tiêu đề dạng câu hỏi | ✓ | ✓ | ✓ | ✓ |
| Màu đỏ chỉ để cảnh báo | ✓ | ✓ | ✓ | ✓ |
| Định dạng có điều kiện | ✓ | ✓ | ✓ | ✓ |
| Slicer phân cấp | ✓ | ✓ | ✓ | ✓ |
| OLAP drill-down / roll-up | ✓ | ✓ | ✓ | ✓ |
| Drill-through | – | – | ✓ | ✓ |
| Tooltip | ✓ | ✓ | ✓ | ✓ |
| Chuỗi thời gian có dự báo | ✓ | – | – | – |
| Thống kê: Key Influencers | – | ✓ | – | – |
| Publish web và mã QR | ✓ | ✓ | ✓ | ✓ |

Mỗi mục có ít nhất một dashboard đáp ứng: dự báo ở DB1, Key Influencers ở DB2, OLAP drill-down ở DB3, drill-through ở DB3 và DB4. Định dạng số, tiêu đề câu hỏi, màu đỏ cảnh báo và định dạng có điều kiện áp dụng cho cả bốn dashboard.

## 3. Hướng dẫn chi tiết

**Định dạng số.** Chọn visual → *Format → Display units* (Thousands, Millions) và *Value decimal places = 1*; với measure dùng *Measure tools → Format → Custom*: `#,0.0,,"M"` (triệu), `#,0.0,"K"` (nghìn), `0.0%` (phần trăm một chữ số thập phân). Dấu phân cách hàng nghìn bật ở *Format → Value*. Luôn ghi đơn vị (BRL, ngày, %) ở tiêu đề hoặc nhãn trục.

**Tiêu đề dạng câu hỏi.** Mỗi visual có tiêu đề là câu hỏi nó trả lời (mục 7 của từng DB*.md có danh sách); tiêu đề trang cũng là câu hỏi chính của dashboard.

**Màu đỏ chỉ để cảnh báo.** Đỏ (`bad` trong `theme.json`) chỉ dùng cho giá trị xấu hoặc vượt ngưỡng qua định dạng có điều kiện; bảng màu dữ liệu của chủ đề không còn đỏ.

**Định dạng có điều kiện.** Dùng measure DAX trả về mã màu (`Color On-time rate`, `Color Cancel rate`…, xem `powerbi/measures.md` mục 6) và gán qua *Conditional formatting → Field value*.

**Slicer phân cấp và OLAP drill-down.** Slicer thời gian: kéo `Năm → Quý → Tháng` vào một slicer (kiểu phân cấp); slicer địa lý: `Vùng → Bang`. Với biểu đồ, ma trận và bản đồ, bật *Drill* (mũi tên) và *Expand all down one level in the hierarchy*; thao tác này tương ứng roll-up và drill-down của OLAP (`sql/60_olap_examples/`).

**Drill-through.** Tạo trang chi tiết, kéo trường cần lọc vào ô *Drill through → Add drill-through fields here*; người xem chuột phải một điểm → *Drill through*. Nút Back được thêm tự động hoặc chèn bằng *Insert → Buttons → Back*. DB3: trang Chi tiết bang; DB4: trang Chi tiết seller.

**Tooltip.** Tạo trang mới, *Format → Page information → Allow use as tooltip = On*, *Page size = Tooltip*; đặt vài visual nhỏ (card, cột); ở visual nguồn, *Format → Tooltips → Type = Report page* và chọn trang tooltip.

**Chuỗi thời gian có dự báo (DB1).** Chọn line chart GMV theo tháng → ngăn *Analytics* → *Forecast → Add* → *Forecast length = 3 points*, *Confidence interval = 95%*. Dữ liệu chỉ có 20 tháng (2017-01 → 2018-08) và mùa vụ theo năm chưa đủ dữ liệu để kết luận (báo cáo mục 3.1), nên dự báo chỉ để thấy hướng đi; ghi chú cạnh biểu đồ.

**Key Influencers (DB2).** Visual AI của Power BI: chọn *Key influencers*, đặt *Analyze* và *Explain by* theo `powerbi/model.md` mục 8 (DB2 trang 3). Kết quả cho biết yếu tố nào đi kèm review tiêu cực; không chứng minh nhân quả.

**Publish web và mã QR.** Publish theo `powerbi/model.md` mục 9 (File → Embed report → Publish to web). Mã QR: mở link công khai trong Microsoft Edge → menu ⋯ → *Share* → *Create QR code for this page* (hoặc công cụ tạo QR bất kỳ), lưu ảnh `figures/4_qr_dashboard.png` (nhóm tạo sau khi publish) và đặt vào slide cuối và báo cáo.

## 4. Trạng thái
Chưa có file `.pbix` nào được dựng ở thời điểm P8b; các mục trong ma trận là yêu cầu cho người dựng. Sau khi dựng, đánh dấu từng mục ở mục 10 của DB*.md và đặt ảnh chụp tên `4_DBx_<mô-tả>.png` vào `figures/`.
