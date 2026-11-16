# P8d – Tài liệu mô tả và hướng dẫn cho từng người

## Chuẩn bị
- Đọc trước: `CLAUDE.md`, `docs/doi-chieu-nhom6.md`, `huong-dan/00-BAT-DAU-TU-DAY.md`, `huong-dan/dashboards/README.md` và `DB1.md`–`DB4.md`, các handoff P8, P8b, P8c.
- Làm trên nhánh `phase/P8d-huong-dan`, xong thì merge vào `main` và push.
- Không chạy `bootstrap_report.py`, `gen_beamer.py`.

Quy tắc viết:
- Giọng văn trung lập. Không phân loại người đọc theo kỹ năng hay vai trò. Không viết kiểu "dành cho người không biết code".
- Viết bằng tiếng Việt.
- Mọi con số phải lấy từ truy vấn thật hoặc từ handoff đã có.

## Mục tiêu

Mỗi thành viên mở MỘT file là biết đủ những gì cần làm cho phần của mình:
- làm gì;
- cần hiểu gì;
- dùng số liệu và hình nào, ở đâu;
- làm từng bước thế nào;
- nộp gì, nộp ở đâu, hạn nào;
- có thể bị hỏi gì.

## Phân công đã chốt (giữ nguyên, không tự đổi)

Nhóm làm 2 giai đoạn:
- **Giai đoạn 1, trước thuyết trình:** làm slide, sơ đồ draw.io và dashboard.
- **Giai đoạn 2, sau thuyết trình:** viết báo cáo, dựa trên slide của chính mình.

| Người | Mục (báo cáo / slide) | draw.io | Dashboard | Thuyết trình |
| --- | --- | --- | --- | --- |
| Người 1 | Ch.1 lý thuyết rút gọn (slide: tối đa 2 trang trong phần mở đầu) → 2.1 Nghiệp vụ → 2.2 Yêu cầu → 2.3 KPI và cây phân tích | 2 BPMN: `3-2-1_bpmn_don_hang.png`, `3-2-2_bpmn_thu_hut_seller.png` | DB1 Tổng quan và doanh thu | Khảo sát 2.1–2.3 |
| Người 2 | 2.4 Dữ liệu nguồn → 2.5 ERD OLTP → 3.1 Khám phá dữ liệu | `2-4_data_taxonomy`, `2-4_data_flow_hien_trang`, `2-4_data_flow_de_xuat`, `2-5_erd_oltp_gach_chan`, `2-5_data_flow_oltp_olap` | DB2 Giao hàng và trải nghiệm khách | Khảo sát 2.4–2.5, Khám phá dữ liệu |
| Người 3 | 3.2 Kiến trúc → 3.3 ETL → 3.4 Chiều khái niệm → 3.5 Data model | `3-2_kien_truc_cac_lop` (có logo), `3-3_etl_jobs`, `3-5_data_model_logic`, `3-5_data_model_vat_ly`, `3-5_data_mart` | DB3 Địa lý và phí vận chuyển | Kiến trúc, ETL, chiều khái niệm, data model |
| Người 4 | Ch.4 Dashboard: bản đồ bộ dashboard, giới thiệu và demo 4 dashboard, QR; bài học tổng kết của cả nhóm | Bản đồ bộ dashboard | DB4 Thu hút và hiệu quả seller | Dashboard và bài học tổng kết |
| Phú | Mở đầu; Ch.5 Mở rộng (Lakehouse, thu thập API, D8, DB1 trên Superset); kết luận | Kiến trúc Lakehouse | File gốc, D8, ghép file tổng, publish | Mở đầu, mở rộng, kết luận |

Việc riêng thêm:
- Người 2: chạy Excel ToolPak trên `eda_sample.xlsx`, chụp ảnh đối chiếu với sheet `python_doi_chieu`.
- Người 3: chạy mã M trong `powerbi/power-query-vi-du.md`, chụp ảnh before/after.

Thứ tự thuyết trình: Phú mở đầu → Người 1 → Người 2 → Người 3 → Người 4 → Phú (mở rộng, kết luận).

Mốc thời gian:

| Ngày | Việc |
| --- | --- |
| 23/11 | Sơ đồ draw.io và bản nháp slide |
| 25/11 | Bản đầu dashboard; ảnh và 3–5 câu nhận xét gửi Người 4 |
| 26/11 | Mỗi người gửi Người 4 3–5 câu bài học |
| 27/11 | Slide và dashboard xong |
| 28–29/11 | Tập, bấm giờ, tổng duyệt |
| Tuần 12 | Thuyết trình |

Drive gồm các thư mục:
- `01_pBI_data`: CSV.
- `02_Dashboard`: `olist_pbi_2026-11-16.zip` (gồm `olist_base.pbix` và CSV); file riêng `DBx_<tên>.pbix`; ảnh `4_DBx_<mô-tả>.png`.
- `03_drawio`.
- `04_Docs`: `tex-nop/` (nộp file `.tex`), `tham-khao/` (slide nhóm 6).

## Việc cần làm

### 1. Tách file slide theo người
Hiện có file slide do hai người cùng sửa (`01-khao-sat.tex`, `02-phan-tich-thiet-ke.tex`). Tách để **mỗi file slide chỉ có một chủ**, tránh ghi đè khi ghép:
- `01a-nghiep-vu-yeu-cau.tex` (Người 1)
- `01b-du-lieu-nguon-erd.tex` (Người 2)
- `02a-kham-pha.tex` (Người 2)
- `02b-kien-truc-etl-model.tex` (Người 3)
- Giữ các file khác như cũ.

Cập nhật `main.tex` và `slide-script.md`. Biên dịch lại để chắc số trang không đổi.

Làm tương tự với báo cáo nếu còn file chung chủ. Chạy lại `make_overleaf_zip.py` và `make_slides_zip.py` để có zip mới khớp tên file.

### 2. Tạo `huong-dan/phan-viec/`

**`README.md` – phần chung cho cả nhóm:**
- Bảng phân công, lịch, thứ tự thuyết trình (như trên).
- Cách dùng Drive và quy tắc đặt tên file.
- **Power BI:**
  - giải nén zip, mở `olist_base.pbix`, lưu thành `DBx_<tên>.pbix` trước khi dựng (không sửa file gốc);
  - đổi `DataFolder` khi cần Refresh;
  - lấy measure trong thư mục measure;
  - đối chiếu số với bảng giá trị kỳ vọng;
  - chụp ảnh.
- **Slide Beamer trên Overleaf:**
  - tải zip slide, tạo project, chỉ sửa file `.tex` của mình;
  - mẫu một frame thường, frame có hình, frame hai cột, frame có bảng;
  - cách chèn hình từ `figures/`;
  - cách ghi mục barem ở góc;
  - tiêu đề là câu kết luận có số;
  - biên dịch bằng LuaLaTeX;
  - lỗi thường gặp và cách sửa;
  - nộp file `.tex` cùng hình mới vào `04_Docs/tex-nop/`.
- **draw.io:**
  - mở file `.drawio` có sẵn trong `docs/diagrams/`;
  - quy ước màu (fact cam, dimension xanh, …) và font;
  - xuất PNG 200 dpi giữ đúng tên file cũ;
  - nộp `.drawio` và PNG.
- Cách gửi câu hỏi hoặc chỗ chưa hiểu cho Phú.

**`Nguoi-1.md` … `Nguoi-4.md` và `Phu.md`**, mỗi file theo cùng khung:

1. **Phần của bạn:** các mục barem, file slide, sơ đồ, dashboard, phần thuyết trình (khoảng bao nhiêu phút, bao nhiêu slide).
2. **Barem chấm gì ở phần này:** trích các dòng checklist của thầy tương ứng; nhóm 6 được mấy điểm, làm gì (số trang slide nhóm 6), mình làm hơn ở đâu (lấy từ `docs/doi-chieu-nhom6.md`).
3. **Kiến thức cần nắm:** giải thích ngắn bằng lời các khái niệm của phần này, có ví dụ từ dữ liệu Olist. Ví dụ:
   - Người 2: Pareto, Cramér's V và η, STL, IQR và Isolation Forest;
   - Người 3: staging/ODS, surrogate key, SCD2, role-playing, junk dimension, accumulating snapshot, chiều khái niệm.
4. **Số liệu và hình có sẵn:** bảng gồm số liệu chính (giá trị thật), file nguồn (handoff, hình trong `figures/`), dùng ở slide nào.
5. **Danh sách slide đề xuất, slide theo slide:**
   - các cột: số thứ tự | tiêu đề (câu kết luận có số thật) | nội dung chính | hình hoặc bảng | nguồn số liệu | đã có hay cần làm;
   - đối chiếu với frame đang có trong file slide của người đó;
   - khối lượng hợp với thời gian thuyết trình.
6. **Sơ đồ draw.io:** mỗi sơ đồ ghi:
   - phải thể hiện gì;
   - bản nháp hiện có ở đâu;
   - quy ước;
   - lỗi thầy hay bắt (ví dụ kiến trúc không vẽ thành luồng; data flow ghi thông tin, không ghi hành động; ERD gạch chân cột dùng sang OLAP).
7. **Dashboard:** tóm tắt từ `DBx.md`:
   - câu hỏi trả lời, các trang, visual, measure dùng;
   - checklist phải đạt;
   - các bước dựng trong Power BI theo thứ tự;
   - giá trị kỳ vọng để tự kiểm;
   - câu chuyện cần kể khi demo;
   - ảnh cần chụp và tên file.
   - Người 4 thêm: hướng dẫn vẽ bản đồ bộ dashboard, cách gom bài học tổng kết, cách kiểm tra checklist của cả 4 dashboard.
8. **Việc riêng:** ToolPak (Người 2), Power Query (Người 3), gom bài học (Người 4).
9. **Câu hỏi có thể bị hỏi:** lọc từ `huong-dan/04-cau-hoi-van-dap.md` các câu thuộc phần này, kèm câu trả lời ngắn. Bổ sung câu mới nếu phần đó còn thiếu.
10. **Giai đoạn 2 (sau thuyết trình):** các file `report/chapters/...` của người đó, số trang dự kiến, các `\todo` hiện có (đếm thật, liệt kê theo file).
11. **Checklist trước khi nộp và mốc hạn.**

**`Phu.md`** viết dạng checklist cho Phú:
- file gốc, D8, ghép file tổng, publish, QR;
- Superset;
- slide mở đầu, slide chương 5 theo kiến trúc → triển khai → minh chứng → kết quả;
- ghép slide, tổng duyệt;
- giai đoạn 2.

### 3. Bản PDF để đọc nhanh
- Nếu có `pandoc`, xuất mỗi file người ra `exports/huong-dan-ca-nhan/Nguoi-x.pdf` để Phú đưa lên Drive. Thư mục `exports/` không commit.
- Không có `pandoc` thì bỏ qua và ghi chú lại.

### 4. Cập nhật liên kết
- Thêm `huong-dan/phan-viec/` vào bản đồ tài liệu trong `huong-dan/00-BAT-DAU-TU-DAY.md`.
- Chạy `check_md_links.py`.

### 5. Kết thúc
- Viết `handoff/2026-11-16-P8d.md`.
- Commit, merge, push.

Báo lại cho Phú:
- danh sách file đã tạo;
- số slide đề xuất của từng người;
- các file slide đã tách và zip mới;
- các file PDF (nếu có).
