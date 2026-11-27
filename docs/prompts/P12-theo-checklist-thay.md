# P12 – Sửa slide theo nhận xét của thầy cho các nhóm trước

## Nguồn
- `attach/dont do this/checklist.jpg` và `diem.jpg`: nhận xét chi tiết và điểm của thầy cho **nhóm 11 (CRM)**. Dòng có ☞ là lỗi hoặc thiếu. Điểm thấp ở Requirement 1, Data exploration 2, Kiến trúc 2, ETL 1, Dimension 0, Data model 1, Dashboard 2, bài học 0.
- `attach/dont do this/Nhóm 11 - DWBI - CRM.pdf`: slide của chính nhóm đó, xem để hiểu vì sao bị trừ điểm:
  - đầu trang ghi "3. Hệ thống dữ liệu" nhưng nội dung là cây phân tích dashboard;
  - bảng KPI nằm sau data model;
  - mỗi phần kiến trúc, ETL, dimension, data model chỉ 1–5 slide, thiếu mục checklist;
  - biểu đồ EDA không có nhận xét;
  - dashboard chỉ có ảnh chụp, không có câu chuyện;
  - không có bài học.
- `attach/dont do this/Nhóm 15 - BTN Kho dữ liệu.pdf`: slide một nhóm khác bị nhận xét "dùng AI nên trình bày loạn": mỗi phần một kiểu trình bày, nhiều hộp chữ nhỏ trên một trang, còn sót lorem ipsum.
- Thư mục `attach/` không commit. Không chép chữ, số hay hình của các nhóm này.

Làm trên nhánh `phase/P12-checklist`. Xong thì merge vào `main` và push.

## Bước 0
- Nếu `04_Docs/tex-nop/` (Phú tải về `attach/tex-nop/`) có file mới của thành viên: ghép nội dung vào `slides/sections/` trước, rồi mới sửa theo các bước dưới.
- Không có thì bỏ qua bước này.

## 1. Tiêu đề theo đúng tên mục của thầy (đổi quy tắc R1)
Thầy chấm theo checklist: nhìn tiêu đề để biết slide thuộc mục nào. Tiêu đề dạng câu kết luận dài làm thầy khó tìm mục, và đọc giống chữ do AI viết.

- **Quy tắc mới:** tiêu đề = **tên mục trong checklist** + ": " + kết luận ngắn (tuỳ chọn). Tối đa 65 ký tự.
  - Ví dụ: "Data taxonomy: 11 bảng chia 4 nhóm"; "Tần suất cập nhật dữ liệu"; "Thống kê đặc trưng (Excel ToolPak)".
  - Con số chi tiết để ở `\KetLuan`.
- **Danh sách tên mục** (lấy đúng chữ trong checklist, giữ tiếng Anh nếu thầy dùng tiếng Anh):
  - **Khảo sát:** Quy trình nghiệp vụ · Điểm phân tích trên quy trình · Mô hình kinh doanh · Liên kết mô hình kinh doanh – dashboard · Cây nghiệp vụ · Hiện trạng và yêu cầu cải tiến · Yêu cầu phân tích tổng thể (theo chủ điểm) · Mindmap yêu cầu · Cây phân tích dashboard Dx · Bảng KPI · Quy mô dữ liệu · Data flow · Tần suất cập nhật · Data taxonomy · ERD OLTP.
  - **Data exploration:** Chất lượng dữ liệu · Phân bố · Thống kê đặc trưng · Tương quan · Khuynh hướng và mùa vụ.
  - **Thiết kế:** Kiến trúc · Tóm tắt ETL · ETL jobs · Before – after · OLTP → OLAP: <bảng> · Số dòng mỗi dimension · Nhóm dimension · Hệ thống chiều khái niệm · Data model logic · Data model vật lý · Data mart.
  - **Dashboard:** Dx – Tình huống · Dx – Dashboard · Dx – Phát hiện · Dx – Quyết định.
- Cập nhật `slides/QUY-TAC-TRINH-BAY.md` (R1) và `scripts/kiem_tra_slide.py` (giới hạn 65 ký tự) cho khớp.

## 2. Cha – con phải khớp (lỗi đầu tiên thầy ghi)
Nhận xét của thầy: "tiêu đề các mục lẫn lộn: cha là hệ thống dữ liệu nhưng con là yêu cầu phân tích". Rà mọi frame: nội dung phải đúng mục cha (`\subsection` và nhãn `\muc`). Các chỗ đã thấy:

- **`01a`:**
  - "Sáu nhóm câu hỏi phân tích…" đang nằm trong 2.1 Nghiệp vụ → chuyển sang 2.2.
  - "Tám điểm hiện trạng… tám yêu cầu cải tiến" → đặt đầu 2.2.
  - "Phễu 8.000 MQL → 842 deal → 379 seller" là kết quả phân tích dữ liệu → chuyển sang 3.1 (Tương quan) hoặc DB4. Trong 2.1 chỉ giữ quy trình.
- **`01b`:** slide đầu "Phạm vi 01/2017–08/2018 chiếm 99,6% số đơn" là kết quả khám phá → chuyển sang 3.1 (Phân bố), hoặc sang trang "giới hạn dữ liệu" ở 2.2.
- **Tên phần:** đặt theo barem.
  - Khảo sát;
  - Phân tích và thiết kế;
  - **Xây dựng chương trình (Dashboard, bài học)** thay cho "Dashboard và BI";
  - Mở rộng.
  - Mục lục ở slide 2 và nhãn `\muc` đổi theo.
- **Thứ tự Khảo sát theo checklist:**
  1. Quy trình nghiệp vụ, điểm phân tích trên quy trình (A1–A11), chỉ số theo từng bước.
  2. Mô hình kinh doanh, liên kết mô hình kinh doanh – dashboard.
  3. Cây nghiệp vụ.
  4. Hiện trạng → yêu cầu cải tiến; yêu cầu tổng thể theo chủ điểm; mindmap; cây phân tích từng dashboard; bảng KPI; giới hạn dữ liệu.
  5. Nguồn dữ liệu: quy mô, data flow, tần suất cập nhật (biểu đồ theo thời gian → đề xuất công nghệ), taxonomy có ví dụ giá trị thật.
  6. ERD OLTP.

## 3. Data exploration theo đúng thứ tự thầy yêu cầu
Thầy ghi: "trình bày theo thứ tự phân bố → đặc trưng → tương quan → khuynh hướng/mùa". `02a` hiện đang trộn: ngoại lai đứng sau tương quan; Cramér's V tách khỏi các slide tương quan; Haversine nằm giữa phần khám phá.

- **Sắp lại `02a` thành 5 khối,** nhãn `\muc` riêng mỗi khối, mỗi khối mở bằng một slide tiêu đề nhỏ:
  1. **Chất lượng dữ liệu:** lỗi chia 3 nhóm, tỷ lệ rỗng, toạ độ trùng.
  2. **Phân bố:** histogram giá, phí, lead time; phân bố theo thời gian; Pareto danh mục và seller.
  3. **Thống kê đặc trưng:** bảng mean, median, độ lệch, nhọn; ngoại lai IQR và Isolation Forest; ảnh Excel ToolPak đối chiếu Python (khung chờ của Người 2).
  4. **Tương quan:** fact–fact (scatter), dim–fact (giao trễ và review, vùng và trễ, η), dim–dim (Cramér's V); funnel và bán hàng.
  5. **Khuynh hướng và mùa vụ:** GMV theo tháng, Black Friday, STL.
- **Kết thúc khối 5:** "Sáu quyết định thiết kế đến từ khám phá dữ liệu".
- **Haversine (3 slide):** chuyển sang 3.3 ETL (bước làm giàu `distance_km`) hoặc `99-du-phong.tex`. Không để trong khám phá.
- **Mỗi biểu đồ có một câu nhận xét** (`\KetLuan`). Thầy trừ điểm khi thiếu "bình luận phân tích các biểu đồ".
- **Đa dạng loại biểu đồ:** histogram, boxplot, Pareto, scatter, heatmap, line. Nếu một khối chỉ có một loại, thêm loại khác từ dữ liệu đã có (`analysis/`, `figures/`).

## 4. Dashboard: kể chuyện và đủ checklist
- **Mỗi dashboard theo mạch Tình huống → Dashboard → Phát hiện → Quyết định** (4 slide):
  - **Tình huống:** ai dùng, câu hỏi gì.
  - **Dashboard:** ảnh lớn.
  - **Phát hiện:** 3 phát hiện có số.
  - **Quyết định:** hành động đề xuất.
- **Thêm vào checklist dashboard** (`huong-dan/dashboards/README.md`, `DB1–4.md`, ma trận): mỗi trang có thanh tiêu đề, icon minh hoạ, **menu điều hướng** giữa các trang (nút page navigator), tiêu đề mỗi đồ thị.
- **Định dạng số theo "con số có nghĩa":** phần trăm trên thẻ KPI làm tròn số nguyên (93%), một chữ số thập phân chỉ khi dưới 10% hoặc cần phân biệt; tiền rút gọn (13,5 triệu). Sửa mục "Định dạng số" và bảng giá trị kỳ vọng.
- **Sửa số cũ:** slide "Mô hình Power BI có 16 bảng và 32 quan hệ" sai → lấy số thật của mô hình hiện tại, hoặc nói rõ là riêng mô hình DB1–DB4.

## 5. Tránh dấu hiệu "làm bằng AI"
- Không còn chữ giữ chỗ khi thuyết trình.
  - Liệt kê mọi `\khungchen` (đang có 47) và `\canxacnhan` (2) theo file và người phụ trách vào handoff.
  - Thêm cờ `--final` cho `kiem_tra_slide.py`: báo LỖI nếu còn `\khungchen`, `\canxacnhan`, `\todo`, "TODO", "lorem".
- **Câu chữ:**
  - viết như người nói, câu ngắn;
  - không dùng dấu "—";
  - không lặp mẫu "không chỉ… mà còn", "đóng vai trò then chốt";
  - thuật ngữ thống nhất một cách gọi trong cả bộ (ví dụ luôn "Data exploration" hoặc luôn "Khám phá dữ liệu", theo cách thầy gọi trong checklist).
- **Mỗi slide một ý,** không nhồi nhiều hộp nhỏ (lỗi của bộ slide nhóm 15).
- **Một phong cách cho cả bộ:**
  - cùng màu fact/dimension;
  - cùng kiểu bảng (`BangTC`);
  - cùng kiểu ảnh chụp (`AnhChup`);
  - sơ đồ draw.io cùng font.

## 5b. Đủ mục ở từng phần thiết kế và bài học (nhóm 11 mất điểm vì thiếu)
Mỗi mục sau phải có slide riêng, tiêu đề đúng tên mục:
- **Kiến trúc:** sơ đồ có logo công nghệ, trang giải thích từng lớp.
- **ETL:** tóm tắt các hoạt động ETL; ETL jobs; before–after; đa dạng công cụ (SQL, Python, Power Query); OLTP → OLAP cho từng dimension và fact.
- **Dimension:** bảng số dòng mỗi dimension; nhóm dimension; hệ thống chiều khái niệm có số giá trị mỗi cấp.
- **Data model:** logic, vật lý, data mart; fact và dimension khác màu; bố cục cân đối.
- **Bài học tổng kết:** tối thiểu 3 bài học theo vấn đề → con số → cách xử lý (Người 4 gom).

## 7. Học từ hai nhóm được đánh giá cao (nhóm 2 và nhóm 5)
Nguồn: `attach/Nhom2_Electronic.pdf` (206 trang, **cùng bộ dữ liệu Olist**), `attach/Slide_Nhom05_DW_BI.pdf` (213 trang, Healthcare). Chỉ học cách tổ chức và loại nội dung; không chép chữ, số, hình.

Điểm chung của hai nhóm, và việc mình cần làm theo:

1. **Bố cục bám đúng barem.**
   - Mỗi phần mở bằng một trang tiêu đề có **danh sách mục con**, đúng tên mục trong checklist. Ví dụ: "Khám phá dữ liệu › Chất lượng › Đặc trưng › Phân bố › Pareto › Tương quan › Xu hướng và mùa vụ › Đối chuẩn Python với ToolPak".
   - Việc cần làm: thêm danh sách `\subsection` (hoặc danh sách mục) vào trang mở phần của theme. Nếu theme không hỗ trợ thì làm một frame mở phần riêng cho mỗi phần.
2. **Tiêu đề ngắn, gọi đúng tên mục.**
   - Nhóm 5 dùng tên mục: "Sơ đồ quy trình BPMN", "Mô tả quy trình", "Cây phân tích dashboard", "Tần suất…".
   - Nhóm 2 dùng dạng "tên mục: kết luận". Ví dụ: "Quy mô 9 bảng nguồn: …".
   - Trùng với mục 1 của prompt này.
3. **Quy trình gắn với dashboard.** Sau mỗi sơ đồ BPMN có một bảng "Bước | Công việc | Người thực hiện | KPI – Dashboard". Kiểm tra slide A1–A11 của mình đã có cột KPI và dashboard cho từng bước chưa; thiếu thì thêm.
4. **Mỗi dashboard theo cùng một mạch:**
   - ảnh dashboard;
   - "Câu chuyện" (ảnh có chú thích câu hỏi ngay trên hình);
   - "Phát hiện và khuyến nghị" (3–4 phát hiện có số);
   - khung **Quyết định**;
   - một slide **DAX chính** của dashboard đó.

   Phần dashboard cũng có slide "Quy chuẩn định dạng số", "Nguyên tắc thiết kế", "Drill-through / slicer / tooltip", "Publish và QR". Đối chiếu `03-dashboard.tex` và thêm những slide còn thiếu; ảnh để khung chờ cho thành viên.
5. **ETL có bằng chứng cho từng bảng:**
   - bảng ánh xạ OLTP → OLAP cho từng dimension và fact;
   - before–after cho các trường hợp tiêu biểu;
   - bảng số dòng trước và sau ETL;
   - ảnh chụp công cụ (psql, Python, Power Query).

   Đối chiếu `02b` và bổ sung từ dữ liệu đã có.
6. **Dimension:** mỗi dimension chính có một trang gồm các cấp, số giá trị mỗi cấp và vài dòng dữ liệu mẫu. Nếu dài quá thì đưa sang `99-du-phong.tex`; trong phần chính giữ bảng tổng hợp.
7. **Tổng kết đầy đủ** (`05-tong-ket.tex`; nhóm 5 làm 6 trang):
   - kết quả đạt được (số lớn);
   - **đối chiếu với yêu cầu**: mỗi yêu cầu ở 2.2 → KPI hoặc dashboard đáp ứng → đạt hay chưa;
   - kiến thức thu được;
   - bài học kỹ thuật;
   - bài học làm việc nhóm (lấy từ phần Người 4 gom);
   - hạn chế và hướng phát triển.
8. **Một phong cách cho cả bộ:** nền trắng, một màu nhấn, cùng kiểu bảng và cùng kiểu hộp nhận xét. Bộ slide Beamer của mình đã thống nhất; giữ như vậy, không thêm hình trang trí.

**Lưu ý về nhóm 2 (cùng dữ liệu Olist):** nhiều con số sẽ trùng vì cùng một dữ liệu, như vậy là bình thường. Không làm slide riêng để so sánh hay nhấn mạnh điểm khác. Phần funnel, Lakehouse CDC và thu thập API cứ trình bày tự nhiên ở đúng mục của chúng (khảo sát, mở rộng). Không nhắc tên nhóm khác.

## 6. Kiểm tra
- Đối chiếu từng dòng checklist của thầy (cả dòng OK lẫn dòng ☞) và từng điểm ở mục 7 với slide.
- Ghi bảng vào `handoff/2026-11-23-P12-checklist.md` với các cột: mục | dòng checklist | slide số | có/thiếu | ai bổ sung.
- Biên dịch cả bộ: không lỗi, không Overfull.
- `kiem_tra_slide.py --strict` 0 LỖI cho mọi file.
- Xem ảnh xem trước toàn bộ phần đã đổi thứ tự.
- Tạo lại zip và `slides/main.pdf`.

Báo lại cho Phú:
- bảng đối chiếu checklist (mục còn thiếu, ai làm);
- danh sách frame đã chuyển chỗ;
- số trang mỗi phần trước và sau;
- danh sách khung chờ còn lại theo người.
