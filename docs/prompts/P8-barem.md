# P8 – Cập nhật dự án theo barem chấm điểm (13/11/2026)

Đọc `CLAUDE.md` và `docs/DW_DESIGN.md` trước khi làm.

Cách làm việc:
- Làm trên nhánh `phase/P8-barem`.
- Commit sau MỖI mục (A, B, C…); xong thì merge vào `main` và push.
- Nếu hết lượt dùng giữa chừng: dừng sau mục đang làm, ghi tiến độ (mục nào xong, mục nào dở) vào `handoff/2026-11-14-P8.md`, rồi commit.

## Bối cảnh

Thầy chấm theo barem 11 mục, đúng thứ tự sau:
- **Khảo sát:** Quy trình nghiệp vụ · Requirement · Hệ thống / quy mô dữ liệu · ERD OLTP.
- **Phân tích & thiết kế:** Data Exploration · Kiến trúc Data Warehouse · ETL · Dimension (hệ thống chiều khái niệm) · Data model OLAP.
- **Xây dựng chương trình:** Dashboard / BI · Bài học tổng kết.
- Ngoài 11 mục: mức độ thu hút (số người đặt câu hỏi) và điểm bổ sung (hướng mở rộng).
- Barem KHÔNG có mục lý thuyết DW/BI.

Thư mục `attach/` là tài liệu tham khảo:

| File | Nội dung | Cách dùng |
| --- | --- | --- |
| `chamdiem.jpg` | barem | đọc để biết thầy chấm mục nào |
| `muctieu.jpg` | bảng nhận xét mẫu; mỗi dòng là một điểm thầy kiểm tra, dòng đỏ là chỗ nhóm khác bị trừ | đọc để biết thầy kiểm tra gì |
| `DWH-Nhom6.pptx` | slide của một nhóm được đánh giá cao | đọc bằng python-pptx, chỉ để học cách trình bày |

- KHÔNG chép nội dung, số liệu hay câu chữ của nhóm khác.
- `attach/` KHÔNG được commit.

## Quy tắc chung

- Không chạy `scripts/bootstrap_report.py`, `scripts/gen_beamer.py`.
- Không đổi DDL kho. Được thêm view hoặc script để làm thống kê.
- Mọi số liệu phải lấy từ truy vấn thật.
- Hình nháp ghi chữ BẢN NHÁP để nhóm biết cần vẽ lại.
- Giọng văn trung lập, không phân loại người đọc theo kỹ năng hay vai trò. Tài liệu viết bằng tiếng Việt.
- Đoạn thành viên đã viết trong file `.tex`: giữ nguyên chữ, chỉ được di chuyển.

## A. Dọn đầu

- Thêm `attach/` vào `.gitignore`.
- Kiểm tra `git status` không còn file nào thuộc `attach/`.

## B. Sắp lại báo cáo và slide theo thứ tự barem

Quy tắc khi đổi tên và gộp file:
- Dùng `git mv` để giữ lịch sử.
- Mỗi mục cấp 2 (x.y) là một file.
- Mục gộp từ nhiều file cũ: nối nội dung theo thứ tự cũ. Giữ `\label` cũ, hoặc nếu đổi thì sửa mọi `\ref` tương ứng.
- Hình: giữ nguyên tên file cũ, vì nhóm đang vẽ lại theo đúng tên đó. Hình mới đặt tên theo số mục mới.

**Báo cáo – `report/chapters/`:**

| File mới | Lấy từ |
| --- | --- |
| `01-tong-quan-ly-thuyet.tex` | gộp `01-tong-quan-dw` + `02-tong-quan-bi`; thêm `\todo{rút gọn còn khoảng 10 trang}`; không tự xoá đoạn nào |
| `2-1-nghiep-vu.tex` | `3-1-gioi-thieu` + `3-2-1-quy-trinh` |
| `2-2-yeu-cau.tex` | `3-2-2-yeu-cau` |
| `2-3-kpi.tex` | `3-3-5-kpi` |
| `2-4-du-lieu-nguon.tex` | `3-2-3-he-thong-du-lieu` |
| `2-5-erd-oltp.tex` | `3-2-4-erd-oltp` |
| `3-1-kham-pha.tex` | `3-3-1-kham-pha` + phần khoảng cách địa lý của `3-5-2-dia-ly` |
| `3-2-kien-truc.tex` | `3-3-2-kien-truc` |
| `3-3-etl.tex` | `3-3-3-ods` + `3-4-1-moi-truong` + `3-4-2-staging-ods` + `3-4-3-doi-soat-tang-dan` |
| `3-4-chieu-khai-niem.tex` | mới, kèm phần dimension của `3-3-4-thiet-ke-kho` |
| `3-5-data-model.tex` | `3-3-4-thiet-ke-kho` + `3-4-4-mart-olap` + `3-5-1-hieu-nang` |
| `4-dashboard.tex` | `3-4-5-dashboard` |
| `5-1-lakehouse.tex` | khung mới (xem mục F) |
| `5-2-thu-thap-api.tex` | khung mới (xem mục F) |
| `06-ket-luan.tex` | `04-ket-luan` |

- Thứ tự chương: 1 Tổng quan lý thuyết · 2 Khảo sát · 3 Phân tích và thiết kế · 4 Dashboard và BI · 5 Mở rộng · 6 Kết luận.
- Cập nhật `report/main.tex` và `report/README.md`.

**Slide – `slides/sections/`:**

| File mới | Lấy từ |
| --- | --- |
| `00-mo-dau.tex` | tiêu đề, nhóm, mục lục; tối đa 2 slide lý thuyết lấy từ `01-ly-thuyet` |
| `01-khao-sat.tex` | `02-bai-toan` + phần nguồn và ERD của `03-du-lieu` |
| `02-phan-tich-thiet-ke.tex` | phần EDA của `03-du-lieu` + `04-kien-truc` + `05-etl-mart-olap` |
| `03-dashboard.tex` | `06-dashboard` + bài học |
| `04-mo-rong.tex` | khung mới (xem mục F) |
| `05-tong-ket.tex` | `07-ket-luan` |
| `99-du-phong.tex` | `08-du-phong` |

- Mỗi slide hiện mục barem ở góc, ví dụ "2.4 · Dữ liệu nguồn". Dùng `\section` / `\subsection` và headline của theme nếu theme hỗ trợ.
- Tiêu đề slide là một câu kết luận có số.

Cập nhật các file tham chiếu sang tên file mới:
- `slides/slide-script.md`, `slides/README.md`
- `huong-dan/00-BAT-DAU-TU-DAY.md` (lộ trình, bản đồ tài liệu)
- `handoff/00-TONG-QUAN.md` (bảng mục báo cáo → file nguồn → hình)
- mọi chỗ khác còn nhắc tên file cũ

Cuối cùng chạy `scripts/check_md_links.py`.

## C. Khảo sát: số liệu và bản nháp còn thiếu

### C1. Dữ liệu nguồn (mục 2.4)

**Tần suất cập nhật:**
- Biểu đồ theo thời gian: số đơn/ngày (và theo tháng), dòng hàng/tháng, review/tháng, MQL/tháng, deal/tháng.
- Bảng: bảng nguồn | khối lượng trung bình và đỉnh mỗi ngày | tần suất cập nhật | công nghệ xử lý đề xuất.
  - Ví dụ công nghệ: lô hằng ngày dùng procedure PostgreSQL; gần thời gian thực dùng CDC + Kafka (nối sang chương 5).

**Data taxonomy:**
- Cây phân loại 11 bảng nguồn thành 4 nhóm: dữ liệu chủ, dữ liệu giao dịch, dữ liệu tương tác, dữ liệu tham chiếu.
- Mỗi nhánh có ví dụ cột kèm một giá trị thật.
- Bảng phân loại theo kiểu dữ liệu, độ nhạy cảm (định danh, vị trí) và tính biến động.
- Hình: `2-4_data_taxonomy.png`.

**Data flow giữa các hệ thống CNTT:** hai sơ đồ.
- Hiện trạng: marketplace / kênh bán, hệ thống đơn hàng, thanh toán, vận chuyển, đánh giá, marketing funnel (SDR/SR).
  - Mũi tên ghi THÔNG TIN được truyền (đơn hàng, trạng thái giao, thanh toán, đánh giá, lead), KHÔNG ghi hành động.
- Đề xuất: nguồn → staging → ODS → DW → mart → BI.
  - Kèm bảng: lớp | thành phần | công nghệ | tần suất | ghi chú.
- Xuất `.drawio` qua `scripts/gen_drawio.py` và PNG nháp.

### C2. Nghiệp vụ, yêu cầu, KPI (mục 2.1–2.3)

Bản nháp ghi vào `huong-dan/05-nghiep-vu-nhap.md` và file `.tex` tương ứng:
- **Điểm phân tích trên quy trình:** mã A1, A2… gắn bước BPMN → dashboard → KPI → khía cạnh phân tích.
- **Business Model Canvas:** khối Canvas → câu hỏi quản trị → chỉ số → dashboard.
- **Hiện trạng → yêu cầu cải tiến.**
- **Đối tượng sử dụng:** người dùng → câu hỏi → dashboard → tần suất xem.
- **Bảng chủ điểm – khía cạnh – chỉ số.**
- **Giới hạn dữ liệu ảnh hưởng tới KPI:**
  - GMV có hai cách đo
  - Orders khác Orders placed
  - 380 so với 379 seller có đơn
  - năm 2016 thưa, tháng 2018-09 bị cắt
  - đơn có nhiều review

### C3. ERD OLTP (mục 2.5)

- ERD tô màu theo nhóm bảng; gạch chân các cột được dùng sang OLAP (theo `docs/mapping.csv`).
- Bảng tổng hợp mapping OLTP → OLAP.
- Sơ đồ data flow OLTP → OLAP.

## D. Khám phá dữ liệu bổ sung (mục 3.1)

- Script đặt trong `scripts/eda/`, thêm vào `run_all.py`, chạy trên `olist_full`.
- Dùng nhiều loại biểu đồ: boxplot, heatmap, scatter/hexbin, line, Pareto, histogram.
- Mỗi hình kèm 1–2 câu nhận xét.

### D1. Ngoại lai

- Hai cách: IQR (ngưỡng 1,5×IQR) và Isolation Forest (ghi rõ `contamination`, cố định `random_state`).
- Biến: price, freight_value, product_weight_g, lead time, delay.
- Báo: số ngoại lai theo mỗi cách, phần giao nhau, vài dòng ví dụ.
- Kết luận giữ hay loại, và vì sao (ngoại lai hợp lệ hay lỗi dữ liệu).

### D2. Tương quan biến rời rạc

- Cramér's V (có hiệu chỉnh Bergsma) cho cặp biến phân loại: payment_type, category_group, vùng khách, vùng seller, order_status, cờ giao trễ, nhóm review.
- Tỉ số tương quan η (biến phân loại → biến số). Ví dụ: delay theo vùng, review theo nhóm ngành.
- Kèm công thức viết bằng LaTeX, thang đọc kết quả, heatmap.
- Bảng "dùng hệ số nào khi nào": Pearson / Spearman / Cramér's V / η.
- Đối chiếu với kết quả Spearman đã có.

### D3. Khuynh hướng và mùa vụ

- Chuỗi số đơn và GMV theo tuần, theo tháng.
- Phân rã STL (statsmodels) trên đoạn đủ dữ liệu 2017-01 → 2018-08.
- Độ mạnh xu hướng và mùa vụ theo công thức 1 − Var(R)/Var(S+R).
- Heatmap ngày trong tuần × giờ.
- Đỉnh Black Friday 2017.
- Nêu rõ giới hạn: dữ liệu dưới 2 năm nên mùa vụ theo năm yếu.

### D4. Thống kê đặc trưng

- Bảng: mean, median, std, skew, kurtosis, min, max.
- Xuất file Excel mẫu để nhóm chạy Data Analysis Toolpak, kèm sẵn số tính bằng Python để đối chiếu.
- Cập nhật `handoff/excel-toolpak-guide.md`.

### D5. Từ điển dữ liệu nguồn

- 11 bảng; mỗi cột ghi kiểu, miền giá trị, % null, vai trò trong DW.
- Bỏ qua nếu đã có đủ.

Kết quả mục D ghi vào `handoff/2026-11-14-P8-eda.md`: số liệu và câu nhận xét cho từng hình.

## E. Phân tích và thiết kế (mục 3.2–3.5)

### E1. Kiến trúc

- Bảng các lớp: thành phần, công nghệ, số bảng, số dòng, tần suất.
- Sửa `docs/diagrams/kien-truc-cac-lop.drawio` thành hình THEO LỚP: các khối xếp tầng, mỗi lớp liệt kê thành phần. Không vẽ thành luồng.
- Có ô logo công nghệ: PostgreSQL, Python, Power BI, GitHub. Không tải được logo chính thức thì để ô chữ.

### E2. ETL

- Bảng tóm tắt: giai đoạn → nội dung → công cụ → kết quả (số dòng thật lấy từ `etl_log`).
- Sơ đồ các job của `run_pipeline` (tên job, thứ tự, bảng vào/ra), sinh từ `etl_log.job_run`.
- Bảng kết quả nạp kho: bảng, loại, số cột, số dòng, đối chiếu.
- Thêm `powerbi/power-query-vi-du.md`:
  - một quy tắc làm sạch viết lại bằng Power Query M: chuẩn hoá tên thành phố (bỏ dấu, chữ thường), zip đủ 5 ký tự;
  - hướng dẫn chụp before/after trong Power BI;
  - mục đích: đủ yêu cầu dùng cả Power Query, Python và SQL.

### E3. Hệ thống chiều khái niệm

Với mỗi dimension, lập bảng:
- cột = các cấp phân cấp;
- ô = vài giá trị ví dụ;
- dòng cuối = số giá trị phân biệt mỗi cấp (truy vấn thật).

Kiểm tra phân cấp có đúng không:
- tháng phải đi kèm năm;
- city phải đi kèm state (đếm thật số tên city trùng nhau giữa các bang);
- product → category → category_group;
- lead_origin → nhóm kênh.

Chia dimension thành các nhóm:
- conformed / dùng chung
- role-playing (date)
- SCD2 (customer)
- junk (lead_profile)
- danh mục nhỏ

Bổ sung vào `DW_DESIGN.md` nếu còn thiếu.

### E4. Data model

Ba hình:
- **Logic:** 6 quy trình (fact) → dimension → các cấp; không ghi kiểu dữ liệu.
- **Vật lý tổng thể:** mọi bảng `dw` với cột, kiểu, PK, FK, sinh từ `information_schema`; fact và dim khác màu.
- **Data marts:** 4 mart; mỗi mart gồm fact, các dim và 3–4 câu hỏi phân tích.

Cập nhật `docs/diagrams/data-model-theo-mart.drawio` và PNG nháp.

### E5. Hiệu năng

Chuyển nội dung hiệu năng (`handoff/2026-11-05-P7-perf.md`) vào mục 3.5.

## F. Khung chương 5 Mở rộng

- `5-1-lakehouse.tex`: kiến trúc → triển khai → kết quả.
- `5-2-thu-thap-api.tex` (thu thập dữ liệu thực tế từ API): bài toán → kiến trúc → triển khai → kết quả.
- Slide `04-mo-rong.tex`: cùng thứ tự với hai file trên.
- Nội dung để `\todo`; P9 (API) và P10 (Lakehouse) sẽ điền.

## G. Dashboard và bài học

**Checklist chung** trong `huong-dan/dashboards/` (README hoặc đầu `D1.md`):
- định dạng số: K/M, phần trăm 1 chữ số thập phân, dấu phân cách;
- tiêu đề dạng câu hỏi;
- màu đỏ chỉ dùng để cảnh báo;
- định dạng có điều kiện;
- slicer phân cấp và drill-down (OLAP);
- drill-through, tooltip;
- chuỗi thời gian có dự báo;
- publish web và mã QR.

Rà từng file `D*.md`: ghi rõ dashboard đáp ứng mục nào trong checklist.

**Bản nháp "Bài học"** trong `4-dashboard.tex`:
- Về chỉ số:
  - GMV 13,49 so với 13,59 triệu;
  - Orders so với Orders placed;
  - review đúng hạn sửa từ 4,21 thành 4,29;
  - 380 so với 379 seller.
- Về quy trình:
  - khoá thay thế từng không cố định giữa các lần dựng;
  - sửa ở ETL, không sửa ở BI;
  - số liệu trong tài liệu sinh từ database.

## H. Vấn đáp

Thêm câu hỏi vào `huong-dan/04-cau-hoi-van-dap.md`:
- ngoại lai
- Cramér's V và η (có công thức)
- STL
- chiều khái niệm
- taxonomy
- data flow
- vì sao kiến trúc vẽ theo lớp

## I. Sinh lại, kiểm tra, bàn giao

1. Chạy EDA, `export_latex` và các script `gen_*` liên quan.
2. Biên dịch báo cáo (XeLaTeX) và slide (LuaLaTeX).
3. Chạy `check_md_links.py`.
4. Viết `handoff/2026-11-14-P8.md` theo mẫu handoff.
5. Commit theo từng mục, merge, push.

Báo lại cho Phú:
- bảng đổi tên file: cũ → mới;
- số trang báo cáo và số trang slide;
- các số mới chính: số ngoại lai, Cramér's V lớn nhất, độ mạnh mùa vụ, số tên city trùng;
- danh sách hình mới;
- việc còn lại để nhóm vẽ lại hoặc viết lại.
