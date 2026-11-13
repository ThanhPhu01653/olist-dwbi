# Đối chiếu với slide nhóm 6 theo barem

## Mục đích và nguồn
- **Nguồn:** slide nhóm 6 (Finance Services, 238 trang) để ở Drive `04_Docs/tham-khao/`, cùng ảnh điểm của nhóm.
- **Dùng để làm gì:** biết mỗi mục barem cần có loại nội dung nào. Phần của mình làm cùng loại phân tích, nhưng trên dữ liệu Olist và bằng số liệu của mình.
- **Không được:** chép câu chữ, số liệu hay hình của nhóm 6.

Điểm của nhóm 6 (thang 5):
- Quy trình 5 · Requirement 4,5 · Hệ thống dữ liệu 4,5 · ERD 5
- EDA 4 · Kiến trúc 4 · ETL 5 · Dimension 4 · Data model 5
- Dashboard 3,5 · Bài học 4 · Điểm bổ sung 2

## Bảng đối chiếu

### Quy trình nghiệp vụ (2.1, Người 1)
- **Nhóm 6 (5 điểm, slide 4–14):**
  - Tổng quan 4 quy trình; mỗi quy trình con một trang BPMN.
  - Bảng "điểm phân tích trên quy trình": mỗi điểm ghi bước → dashboard → KPI → khía cạnh.
  - Cây nghiệp vụ; Business Model Canvas.
  - Bảng nối từng khối Canvas → câu hỏi → chỉ số → dashboard.
- **Dự án đã có:** 2 BPMN nháp, Canvas, cây nghiệp vụ, các bảng nháp từ P8 trong `huong-dan/05-nghiep-vu-nhap.md`.
- **Cần làm:**
  - Tách mỗi quy trình con (đặt hàng → duyệt → giao → đánh giá; thu hút seller) thành một trang.
  - Đánh dấu điểm A1, A2… ngay trên hình BPMN.
  - Bảng điểm phân tích và bảng Canvas → dashboard trỏ tới DB1–DB4.

### Requirement (2.2–2.3, Người 1)
- **Nhóm 6 (4,5 điểm, slide 15–22):**
  - Hiện trạng → yêu cầu cải tiến (chia chức năng và phi chức năng).
  - Đối tượng sử dụng × câu hỏi × dashboard × tần suất.
  - Bảng chủ điểm – khía cạnh – chỉ số.
  - Cây yêu cầu; cây phân tích từng dashboard.
  - Trang "lưu ý giới hạn dữ liệu" ghi vấn đề và cách xử lý.
- **Dự án đã có:** cây yêu cầu, 4 cây phân tích DB1–DB4, bảng KPI.
- **Cần làm:**
  - Thêm yêu cầu phi chức năng (thời gian làm mới, thời gian phản hồi, ẩn dữ liệu định danh).
  - Trang giới hạn dữ liệu theo dạng vấn đề → cách xử lý. Ví dụ:
    - GMV hai cách đo;
    - Orders khác Orders placed;
    - 380 so với 379 seller;
    - năm 2016 thưa, tháng 2018-09 bị cắt;
    - đơn có nhiều review.

### Hệ thống / quy mô dữ liệu (2.4, Người 2)
- **Nhóm 6 (4,5 điểm, slide 23–36):**
  - Thông tin chung; quy mô từng bảng.
  - Biểu đồ tần suất và khối lượng cập nhật; công nghệ đề xuất theo tần suất.
  - Taxonomy chia master / transaction / interaction / reference, có ví dụ giá trị thật.
  - Data flow hiện trạng và đề xuất; danh mục các luồng; bảng các lớp.
  - Đánh giá chất lượng sơ bộ.
- **Dự án đã có (P8):** biểu đồ tần suất, taxonomy, data flow hiện trạng và đề xuất (bản nháp).
- **Cần làm:**
  - Trang danh mục luồng: luồng, nguồn → đích, thông tin, tần suất.
  - Trang đánh giá chất lượng sơ bộ trước khi vào EDA.
  - Vẽ lại sơ đồ bằng draw.io.

### ERD OLTP (2.5, Người 2)
- **Nhóm 6 (5 điểm, slide 37–41):** ERD vật lý; bảng các quan hệ; gạch chân cột dùng sang OLAP; tổng hợp mapping; data flow OLTP → OLAP.
- **Dự án đã có (P8):** ERD gạch chân, mapping 65/71 cột, data flow OLTP → OLAP.
- **Cần làm:** thêm trang bảng các quan hệ (bảng cha → bảng con, khoá, bội số); vẽ lại bằng draw.io.

### Data Exploration (3.1, Người 2)
- **Nhóm 6 (4 điểm, slide 43–105):** 6 bước.
  - Chất lượng: lỗi chia 3 nhóm (khoá & định dạng / thiếu / logic, ngoại lai, dư thừa), toàn vẹn tham chiếu.
  - Từ điển dữ liệu.
  - Phân bố và Pareto.
  - Thống kê đặc trưng bằng Excel và R, đối chiếu với Python.
  - Tương quan fact–fact / dim–fact / dim–dim.
  - Khuynh hướng và mùa vụ, có STL.
- **Dự án đã có (P8):** đủ 6 bước; ngoại lai IQR và Isolation Forest; Cramér's V và η; STL; file ToolPak.
- **Cần làm hơn nhóm 6** (nhóm 6 mất điểm ở phần này dù có 63 slide):
  - Mỗi biểu đồ một câu nhận xét.
  - Công thức rõ cho biến rời rạc.
  - Số ngoại lai báo theo từng biến và số dòng không trùng.
  - Chụp ảnh đối chiếu ToolPak với Python.

### Kiến trúc DWH (3.2, Người 3)
- **Nhóm 6 (4 điểm, slide 106–107):** một hình kiến trúc theo lớp, mỗi lớp liệt kê thành phần.
- **Dự án đã có (P8):** hình theo lớp (nháp), bảng các lớp.
- **Cần làm hơn nhóm 6:**
  - Thêm một trang giải thích từng lớp và lý do chọn công nghệ.
  - Logo công nghệ.
  - Không vẽ thành luồng.

### ETL (3.3, Người 3)
- **Nhóm 6 (5 điểm, slide 108–128):**
  - Bảng tóm tắt các giai đoạn (công cụ, kết quả).
  - ETL từng bảng nguồn → staging; mô hình pipeline các job.
  - OLTP → OLAP cho từng dimension và từng fact, mỗi bảng một trang.
  - Ví dụ một bản ghi đi vào kho; kết quả nạp có đối chiếu số dòng.
- **Dự án đã có:** tóm tắt, sơ đồ job, before–after 6 bảng, 1 đơn thật đi qua các lớp, giám sát ETL (từ D7 cũ), Power Query mẫu.
- **Cần làm:**
  - Mỗi dimension và mỗi fact một trang: nguồn, quy tắc, số dòng vào / ra.
  - Chạy mã M trong Power BI, chụp ảnh before/after.

### Dimension (3.4, Người 3)
- **Nhóm 6 (4 điểm, slide 129–131):** bảng giá trị phân biệt theo từng cấp của mọi dimension.
- **Dự án đã có (P8):** bảng cấp và số giá trị; 303 tên thành phố trùng giữa các bang.
- **Cần làm hơn nhóm 6:**
  - Sơ đồ phân cấp.
  - Giải thích cấp nào hợp lệ (tháng phải kèm năm, thành phố phải kèm bang).
  - Nhóm dimension: dùng chung, role-playing, SCD2, junk.

### Data model OLAP (3.5, Người 3)
- **Nhóm 6 (5 điểm, slide 132–134):** mô hình logic; mô hình vật lý; data marts kèm câu hỏi phân tích.
- **Dự án đã có (P8):** 3 hình nháp tương ứng; hiệu năng.
- **Cần làm:** vẽ lại bằng draw.io; fact và dimension khác màu.

### Dashboard (Ch.4, Người 4 và mọi người)
- **Nhóm 6 (3,5 điểm, slide 135–147):**
  - Bảng KPI theo dashboard; thống kê bộ dashboard; publish và QR.
  - Mỗi dashboard: một trang tình huống, rồi một trang dashboard.
  - Trang kỹ thuật dùng.
- **Dự án đã có (P8b):** đặc tả DB1–DB4, ma trận checklist, bảng giá trị kỳ vọng.
- **Cần làm hơn nhóm 6** (nhóm 6 thấp nhất ở mục này):
  - Đủ checklist của thầy: định dạng số, OLAP, dự báo, drill-through, tooltip, định dạng có điều kiện.
  - Mỗi dashboard kể một câu chuyện có số.

### Bài học (Ch.4 và Ch.6, Người 4 và Phú)
- **Nhóm 6 (4 điểm, slide 148–150, 235–237):** bài học về chỉ số và về quy trình; tổng kết quy trình, kiến thức và công cụ.
- **Dự án đã có:** bản nháp bài học bằng ví dụ thật của dự án.
- **Cần làm:** mỗi bài học gồm vấn đề → con số → cách xử lý.

### Mở rộng (Ch.5, Phú)
- **Nhóm 6 (2 điểm bổ sung, slide 151–233):**
  - Lakehouse: kiến trúc → các bước triển khai, mỗi bước kèm một slide minh chứng → kết quả.
  - Trợ lý hỏi đáp Text-to-SQL.
- **Dự án đã có:** khung chương 5.
- **Cần làm:** P9 (thu thập API, D8) và P10 (Lakehouse, DB1 trên Superset); xen kẽ slide triển khai và slide minh chứng.

## Việc rút ra cho từng người

**Người 1**
- Mỗi quy trình con một trang.
- Điểm A1… trên BPMN.
- Yêu cầu phi chức năng.
- Trang giới hạn dữ liệu.

**Người 2**
- Danh mục luồng dữ liệu.
- Đánh giá chất lượng sơ bộ.
- Bảng các quan hệ trong ERD.
- Nhận xét cho từng biểu đồ EDA.
- Ảnh đối chiếu ToolPak với Python.

**Người 3**
- Trang giải thích từng lớp kiến trúc.
- Mỗi dimension và mỗi fact một trang OLTP → OLAP.
- Sơ đồ phân cấp.
- Ảnh Power Query.

**Người 4**
- Trang tình huống trước mỗi dashboard.
- Kiểm tra 4 dashboard đủ checklist.

**Phú**
- Slide minh chứng xen kẽ cho từng bước triển khai ở chương 5.
