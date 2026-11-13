# Hướng dẫn dựng dashboard: checklist chung (P8)

Thư mục này chứa hướng dẫn từng dashboard `D1.md` … `D7.md`. Trang này là **checklist chung** rút từ nhận xét mẫu của barem; mỗi file D*.md có mục 12 ghi dashboard đó đáp ứng từng mục thế nào. Ký hiệu trong ma trận: **✓** đã có trong hướng dẫn, **+** bổ sung ở P8, **✓ +** đã có và bổ sung thêm, **–** không áp dụng (lý do ở mục 12).

## 1. Checklist chung

| Mục | Yêu cầu | Ví dụ / nơi xem |
| --- | --- | --- |
| Định dạng số | mọi số trên dashboard dùng đơn vị rút gọn và dấu phân cách; phần trăm 1 chữ số thập phân | số đơn 12.3K (không phải 12.345); tiền 13.5M; 12,4% (không phải 12,39% hoặc 12%) |
| Tiêu đề dạng câu hỏi | mỗi visual có tiêu đề là một câu hỏi mà visual trả lời | "GMV tháng này tăng hay giảm so với tháng trước?" |
| Màu đỏ chỉ để cảnh báo | đỏ chỉ dùng cho giá trị xấu hoặc vượt ngưỡng; màu dữ liệu thường dùng xanh, cam, tím | theme.json không còn đỏ trong dataColors; đỏ chỉ ở định dạng có điều kiện |
| Định dạng có điều kiện | dùng DAX trả về màu (Color On-time rate…) cho card, bảng, bản đồ | xem mục 7 của từng D*.md và `powerbi/measures.md` |
| Slicer phân cấp và drill-down (OLAP) | slicer theo phân cấp (Năm → Quý → Tháng; Vùng → Bang) và biểu đồ có drill-down / drill-up | Date hierarchy, Geography hierarchy, Product hierarchy trong `powerbi/model.md` |
| Drill-through và tooltip | chuột phải một điểm để nhảy sang trang chi tiết (drill-through); di chuột hiện trang tooltip | trang chi tiết đơn, tooltip theo tháng, bang, kênh |
| Chuỗi thời gian có dự báo | line chart theo tháng có đường dự báo (Analytics → Forecast) để nêu xu thế và mùa | chỉ cho chuỗi đủ dài; nêu rõ giới hạn 20 tháng dữ liệu |
| Publish web và mã QR | publish báo cáo công khai (không cần đăng nhập) và in mã QR của link | `powerbi/model.md` mục 9; mã QR tạo từ link |

## 2. Ma trận đáp ứng

| Mục checklist | D1 | D2 | D3 | D4 | D5 | D6 | D7 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Định dạng số | + | + | + | + | + | + | + |
| Tiêu đề dạng câu hỏi | + | + | + | + | + | + | + |
| Màu đỏ chỉ để cảnh báo | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Định dạng có điều kiện | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Slicer phân cấp và drill-down (OLAP) | ✓ + | ✓ + | ✓ + | ✓ + | ✓ + | ✓ + | ✓ + |
| Drill-through và tooltip | + | + | + | + | + | + | + |
| Chuỗi thời gian có dự báo | + | – | + | – | + | – | – |
| Publish web và mã QR | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

## 3. Hướng dẫn chi tiết

**Định dạng số.** Chọn visual → *Format → Display units* (Thousands, Millions) và *Value decimal places = 1*; với measure, dùng *Measure tools → Format → Custom*: `#,0.0,,"M"` (triệu), `#,0.0,"K"` (nghìn), `0.0%` (phần trăm một chữ số thập phân). Dấu phân cách hàng nghìn bật trong *Format → Value*. Luôn ghi đơn vị (BRL, ngày, %) ở tiêu đề hoặc nhãn trục.

**Tiêu đề dạng câu hỏi.** Mỗi visual có tiêu đề là câu hỏi mà nó trả lời (xem mục 12 của từng D*.md); tiêu đề trang cũng là câu hỏi chính của dashboard.

**Màu đỏ chỉ để cảnh báo.** Đỏ (`bad` trong `theme.json`) chỉ dùng cho giá trị xấu hoặc vượt ngưỡng qua định dạng có điều kiện; bảng màu dữ liệu của theme không còn đỏ.

**Định dạng có điều kiện.** Dùng measure DAX trả về mã màu (`Color On-time rate`, `Color Cancel rate`…, xem `powerbi/measures.md`) và gán qua *Conditional formatting → Field value*.

**Slicer phân cấp và drill-down (OLAP).** Slicer thời gian: kéo `Năm → Quý → Tháng` vào một slicer (kiểu phân cấp); slicer địa lý: `Vùng → Bang`. Với biểu đồ, bật *Drill* (mũi tên) và *Expand all down one level*; thao tác này tương ứng roll-up và drill-down của OLAP (`sql/60_olap_examples/`).

**Drill-through.** Tạo trang chi tiết, kéo trường cần lọc vào ô *Drill through → Add drill-through fields here*; người xem chuột phải một điểm → *Drill through*. Nút quay lại được thêm tự động.

**Tooltip.** Tạo trang mới, *Format → Page information → Allow use as tooltip = On*, *Page size = Tooltip*; đặt vài visual nhỏ (card, cột); ở visual nguồn, *Format → Tooltips → Type = Report page* và chọn trang tooltip.

**Chuỗi thời gian có dự báo.** Chọn line chart theo tháng → ngăn *Analytics* → *Forecast → Add* → *Forecast length = 3 points*, *Confidence interval = 95%*. Dữ liệu chỉ có 20 tháng (2017-01 → 2018-08) và mùa vụ theo năm chưa đủ dữ liệu để kết luận (báo cáo mục 3.1), nên dự báo chỉ dùng để thấy hướng đi; ghi chú điều này cạnh biểu đồ. Phân tích xu thế, mùa tuần và Black Friday đã có sẵn ở `handoff/2026-11-14-P8-eda.md` mục D3 để minh hoạ.

**Publish web và mã QR.** Publish theo `powerbi/model.md` mục 9 (File → Embed report → Publish to web). Mã QR: mở link công khai trong Microsoft Edge → menu ⋯ → *Share* → *Create QR code for this page* (hoặc bất kỳ công cụ tạo QR nào), lưu ảnh và đặt vào slide cuối và báo cáo (`figures/4_qr_dashboard.png`, do nhóm tạo sau khi publish).

## 4. Trạng thái đáp ứng
Các mục **+** là yêu cầu cho người dựng Power BI (chưa có `.pbix` nào được dựng ở thời điểm P8). Sau khi dựng, đánh dấu từng mục trong mục 11 của D*.md và bổ sung ảnh chụp vào báo cáo.
