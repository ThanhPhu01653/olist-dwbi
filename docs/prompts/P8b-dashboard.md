# P8b – Gộp bộ dashboard từ 7 xuống 4

Đọc `CLAUDE.md` trước khi làm. Làm trên nhánh `phase/P8b-dashboard`; xong thì merge vào `main` và push. Trong lần commit đầu, commit luôn thư mục `docs/prompts/`.

Quy tắc chung:
- Không chạy `bootstrap_report.py`, `gen_beamer.py`.
- Giọng văn trung lập.
- Mọi số liệu lấy từ truy vấn thật.
- Đoạn thành viên đã viết: giữ nguyên chữ, chỉ di chuyển.

## Quyết định (ngày 13/11)

Chương 4 chỉ còn 4 dashboard Power BI. Mỗi dashboard thuộc một loại thầy yêu cầu và do một thành viên dựng. Phú làm file gốc, tổng hợp và chỉnh sửa.

| Mới | Gộp từ | Loại | Người dựng |
| --- | --- | --- | --- |
| DB1 – Tổng quan và doanh thu | D1 + D2 | Theo dòng thời gian (có dự báo) | Người 1 |
| DB2 – Giao hàng và trải nghiệm khách | D3 + D5 | Vận hành + thống kê (Key Influencers) | Người 2 |
| DB3 – Địa lý và phí vận chuyển | D4 | OLAP; drill-down vùng → bang → thành phố; drill-through sang trang chi tiết bang; tooltip | Người 3 |
| DB4 – Thu hút và hiệu quả seller | D6 (2 trang) | Vận hành; funnel; drill-through sang trang chi tiết seller | Người 4 |

- **D7 (giám sát chất lượng dữ liệu và ETL):** bỏ khỏi bộ dashboard. Số liệu của nó đưa vào mục 3.3 ETL, thành bảng kết quả nạp và giám sát.
- **D8 (Thị trường Brazil, dữ liệu API):** thuộc chương 5, do P9 làm. P8b chỉ để chỗ cho D8, chưa làm nội dung.

## Việc cần làm

### 1. `huong-dan/dashboards/`
- **Tạo `DB1.md` đến `DB4.md`** theo mẫu các file `D*.md` hiện có. Nội dung gộp từ các file cũ theo bảng trên.
- **Mỗi file gồm:**
  - câu hỏi trả lời, người dùng và tần suất xem;
  - bố cục từng trang;
  - visual, measure, slicer;
  - drill-down, drill-through, tooltip;
  - định dạng có điều kiện;
  - mục "Đáp ứng checklist";
  - mục "Insight gợi ý";
  - bảng giá trị kỳ vọng.
- **Thêm trang drill-through:**
  - DB3: trang chi tiết bang;
  - DB4: trang chi tiết seller.
- **`README.md`:** thêm bảng ma trận "mục checklist × DB1–DB4". Mỗi mục checklist phải có ít nhất một dashboard đáp ứng: dự báo ở DB1, Key Influencers ở DB2, OLAP drill-down ở DB3, drill-through ở DB3 và DB4. Định dạng số và định dạng có điều kiện áp dụng cho mọi dashboard.
- **Xoá file cũ:** `git rm` các file `D1.md` đến `D7.md`.
- **Script sinh tài liệu:** nếu `scripts/gen_dashboard_docs.py` đang sinh các file trên thì sửa script cho đúng bộ mới, rồi chạy lại.

### 2. Power BI
- **`powerbi/measures.md`:** sắp measure theo DB1–DB4. Chạy lại `gen_powerbi_docs.py` để sinh bảng giá trị kỳ vọng theo từng dashboard.
- **Measure chỉ dùng cho D7:** chuyển xuống phụ lục "Giám sát ETL (dùng ở mục 3.3)".
- **`powerbi/model.md`:** sửa danh sách trang.
- **Ảnh chụp dashboard:** đặt tên `4_DBx_<mô-tả>.png`. Cập nhật mọi chỗ đang ghi `3-4-5_Dx_…`.

### 3. Báo cáo và slide
- **`report/chapters/4-dashboard.tex`:**
  - tiểu mục DB1–DB4, gộp chữ của các tiểu mục D1–D7 cũ theo bảng trên;
  - thêm mục "Thống kê bộ dashboard" (số trang, số biểu đồ, số slicer, số measure, để `\todo` chờ số thật);
  - thêm mục "Publish và mã QR".
- **Nội dung D7:** chuyển vào `3-3-etl.tex` thành bảng kết quả nạp và giám sát. Dùng số liệu thật từ `etl_log`: số dòng qua từng lớp, dòng bị loại theo lý do, thời gian 11 đợt nạp, số test đạt.
- **`2-3-kpi.tex`:**
  - 7 cây phân tích dashboard gộp thành 4;
  - nếu hình cây được sinh bằng script thì sinh lại, đặt tên `2-3_cay_phan_tich_DB1…DB4.png`; nếu không thì ghi `\todo` cho Người 1 vẽ;
  - bảng KPI theo dashboard sửa tương ứng.
- **Slide:** sửa `slides/sections/03-dashboard.tex` và phần 2.3 trong `01-khao-sat.tex` theo đúng như báo cáo.
- **Chương 5:** thêm chỗ cho D8 và DB1 trên Superset trong `5-1-lakehouse.tex`, `5-2-thu-thap-api.tex`, `04-mo-rong.tex` (để `\todo`).

### 4. Tài liệu khác
Tìm và sửa trong toàn repo các chỗ còn nhắc D1–D7 hoặc "7 dashboard" / "bảy dashboard":
- `huong-dan/00-BAT-DAU-TU-DAY.md`
- `huong-dan/04-cau-hoi-van-dap.md`
- `handoff/00-TONG-QUAN.md`
- `slides/slide-script.md`
- `docs/doi-chieu-nhom6.md`
- `README.md`
- `docs/prompts/P9-thu-thap-api.md`, `docs/prompts/P10-lakehouse.md` (chỉ sửa tên dashboard, giữ nguyên nội dung)

Không động vào file CSV xuất cho Power BI. Các bảng `etl_log` vẫn xuất như cũ để mục 3.3 dùng.

### 5. Kiểm tra và bàn giao
- Biên dịch báo cáo và slide; chạy `check_md_links.py`.
- Viết `handoff/2026-11-14-P8b.md`.
- Commit, merge, push.

Báo lại cho Phú:
- danh sách file mới / xoá;
- số trang báo cáo và slide sau khi gộp;
- bảng ma trận checklist;
- những hình cần nhóm vẽ lại.
