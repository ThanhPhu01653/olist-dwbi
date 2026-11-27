# P13 – Chuyển bộ slide sang PowerPoint (.pptx) theo khung slide mới

Làm trên nhánh `phase/P13`, commit sau từng bước. Xong thì merge vào `main` và push. **Không xoá** `slides/` (bộ Beamer) và `report/` (báo cáo LaTeX vẫn giữ nguyên).

## Bối cảnh và quyết định của Phú
- **Bỏ mẫu Beamer.** Bộ thuyết trình làm bằng **PowerPoint (.pptx)**, do script sinh ra từ repo. Thành viên không sửa file nữa, chỉ gửi **ảnh và nội dung** cho Phú.
- **Khung slide:** theo `attach/huong-dan-lam-slide.md` (6 phần, công thức số slide, ba mức Nói kỹ / Vừa / Lướt, bảng khung slide mục 7, checklist mục 6). Đây là hướng dẫn phương pháp của nhóm khác: chỉ dùng cách làm, **không chép** câu chữ, ví dụ hay số liệu Synthea trong đó.
- **Nội dung: tạo nội dung mới** bằng cách kết hợp ba nguồn:
  1. nội dung đã kiểm trong `slides/sections/*.tex` (tiêu đề, `\KetLuan`, gạch đầu dòng, bảng, hình, `\note`), cùng handoff và báo cáo;
  2. khung slide và yêu cầu trong `attach/huong-dan-lam-slide.md`;
  3. ảnh và nội dung thành viên gửi về `slides-pptx/nop/` (bước 2).

  Viết lại câu chữ cho hợp khổ PowerPoint và cách nói, nhưng **mọi con số lấy từ số liệu chốt**, không tự đổi.
- **Giao diện đã có sẵn, không thiết kế lại.** Tím pastel (`7E66B8` nền, `6F55A8` chữ nhấn, `3A2C5E` chữ đậm) nhấn vàng pastel (`F2C46D`). Bố cục thoáng, tham khảo cách trình bày của nhóm 5 nhưng màu và chi tiết khác hẳn:
  - `slides-pptx/template/Olist_Nhom19_template.pptx`: 9 layout BIA, CHUYEN_PHAN, NOI_DUNG, NOI_DUNG_KL, HINH, HINH_KL, HAI_COT_KL, PHU_LUC, CAM_ON. Placeholder `muc` (góc trên phải), `tieu_de`, `noi_dung`/`cot_trai`, `chu_thich`, `ket_luan`, `phan` (chân trang trái, ví dụ "Phần 1 · Khảo sát");
  - `layout_spec.json`: tên và `idx` placeholder, vùng tự do để đặt hình, bảng, thẻ, cùng màu và cỡ chữ;
  - `Olist_Nhom19_giao_dien_mau.pptx` và `.pdf`: 12 slide mẫu gồm bìa, thành viên (viên số), mục lục 5 thẻ, chuyển phần, nội dung + hộp tối điểm nhấn, sơ đồ bằng shape, hình + chú thích, bảng, thẻ số, hộp code DAX, phụ lục, cảm ơn.

  `gen_pptx.py` làm như sau:
  - mở template bằng python-pptx, thêm slide theo tên layout, điền placeholder theo `idx`;
  - hình, bảng, thẻ, sơ đồ đặt vào vùng tự do trong spec, **vẽ giống hệt file mẫu** (màu, bo góc, cỡ chữ);
  - nội dung dài hơn vùng thì tách slide, không thu nhỏ chữ.

  Muốn đổi giao diện thì sửa `build.js`, rồi chạy lần lượt `python make_shapes.py`, `node build.js`, `python fix_names.py`. Không sửa tay file template.
- **Thời lượng: 30–35 phút** (khung md ghi 30–45). Tính theo công thức của khung: Nói kỹ 30 s, Vừa 12 s, Lướt 4 s, demo khoảng 120 s. Nếu vượt thì chuyển Vừa → Lướt, hoặc đưa sang phụ lục.
- **Lỗi hiện tại phải tránh:** chữ trong hình bị răng cưa khi chiếu hoặc phóng to (ví dụ sơ đồ "Quy trình thu hút seller", vì hình raster bị phóng). Mục 3 bên dưới đặt quy tắc chống lỗi này.

## Chỗ khung mới mâu thuẫn với những gì nhóm đã chốt: giữ cách của nhóm
- **Tương quan giữa các measure:** dùng **Spearman** (P12c, đã giải thích vì sao không dùng Pearson), không đổi sang Pearson.
- **Dashboard:** mỗi dashboard **1 trang** (P12f), cộng trang drill-through hoặc tooltip ẩn. Mỗi dashboard trong slide có các khối Ảnh dashboard, Câu chuyện, Phát hiện và khuyến nghị, DAX chính.
- **Chủ đề mở rộng:** nhóm có **hai** phần, Lakehouse (5.1) và Thu thập API (5.2), cùng D8. Giữ cả hai trong phần 4 của khung, mỗi phần theo khung chung (lý thuyết → thiết kế → triển khai → thử nghiệm → so sánh → đánh giá), gọn hơn gợi ý 15–25 slide của khung.
- **Tiêu đề:** tên mục theo checklist của thầy + kết luận ngắn (≤ 65 ký tự, quy tắc R1 cũ). Tiêu đề biểu đồ là cụm danh từ có đơn vị, **không đặt dạng câu hỏi**.
- **Chỉ nói cái lớn:** slide Lướt được phép nhiều, nhưng lỗi nhỏ và quyết định nhỏ vẫn để ở ghi chú hoặc phụ lục, không chiếm slide Nói kỹ.

## Bước 1 – Số liệu chốt và khung slide (nguồn duy nhất)
1. **`slides-pptx/so-lieu-chot.xlsx`:** mỗi con số dùng trên slide là một dòng gồm mã (ví dụ `GMV_TOTAL`), giá trị, đơn vị, nguồn (handoff, truy vấn, script). Lấy từ handoff, `powerbi/measures.md` mục kỳ vọng và các bảng `report/tables/`.
2. **`slides-pptx/khung.yaml`** (hoặc `.json`): mỗi slide một mục, gồm:
   - `id`, `phan` (0–5), `muc_nho`, `tieu_de`, `y` (gạch đầu dòng hoặc bảng), `hinh`, `ket_luan`, `ghi_chu` (ghi chú người nói), `nguoi` (Phú, Người 1–4 theo phân công cũ), `cach` (Nói kỹ / Vừa / Lướt), `giay` (30 / 12 / 4), `muc_bc` (mục báo cáo), `trang_thai`.
   - Con số trong chữ viết dạng `{GMV_TOTAL}` để lấy từ file số liệu chốt.
   - Chuyển đổi từ `.tex` bằng script `scripts/tex_sang_khung.py` (đọc frame, `\KetLuan`, `itemize`, `BangTC`, `\HinhLon` / `\AnhChup` / `\khungchen`, `\note`), rồi sắp lại theo khung 6 phần.
   - Frame của `99-du-phong.tex` thành **phụ lục** (cuối file, cách Lướt, không tính giờ).
3. **Đối chiếu khung mới (mục 4 và checklist mục 6 của md) với nội dung đang có.** Mục nào còn thiếu thì thêm slide với `trang_thai: thieu`, nội dung `[__]` và người phụ trách. Ví dụ dự kiến:
   - Thành viên và phân công; Mục tiêu đề tài;
   - Trường dữ liệu từng bảng; Pareto ≥ 3; Before–After ≥ 4 bảng;
   - Lựa chọn fact; Thuộc tính dẫn xuất; Chỉ mục và phân vùng; Cây KPI;
   - Thao tác OLAP (4 ảnh); Đi sâu vấn đề (4 bước); Demo.

   Không bịa số. Số nào lấy được từ kho bằng truy vấn thì tính và thêm vào số liệu chốt, ghi nguồn.
4. **Xuất `slides-pptx/khung.xlsx`** (bảng khung theo mục 7 của md): một dòng mỗi slide, có cột Trạng thái, `SUM` cột Giây, và tổng giờ theo phần.

## Bước 2 – Nhận bài nhóm đã nộp (chạy khi nhóm đã gửi đủ)
Thành viên gửi ảnh và nội dung, Phú đặt vào `slides-pptx/nop/<Nguoi-1 … Nguoi-4>/`. Định dạng tự do: `.docx`, `.md`, `.txt`, `.pptx`, `.tex`, ảnh `.png`/`.jpg`.
1. Đọc hết, lập bảng ghép trong handoff: file nào → slide nào trong `khung.yaml`; nội dung nào không khớp slide nào.
2. **Câu chữ của thành viên:** giữ ý, sửa cho gọn theo quy tắc (tiêu đề ≤ 65 ký tự, chữ ≥ 18 pt).
3. **Số liệu thành viên ghi:** đối chiếu với số liệu chốt.
   - Lệch thì dùng số liệu chốt và liệt kê chỗ lệch cho Phú.
   - Số mới chưa có trong số liệu chốt thì kiểm bằng truy vấn kho, đúng thì thêm vào.
4. **Ảnh:**
   - kiểm độ phân giải theo quy tắc mục 3;
   - ảnh quá nhỏ hoặc mờ thì vẫn dùng, nhưng liệt kê để chụp lại;
   - ảnh Power BI cắt bỏ viền và thanh công cụ.
5. **Mục còn thiếu:**
   - mục **tự làm được từ repo** thì tự làm, không chờ ai: trường dữ liệu từng bảng, bảng quan hệ khoá, dung lượng cập nhật mới, lựa chọn fact, thuộc tính dẫn xuất, xây `dim_date`, cây KPI, DAX cảnh báo (`SWITCH` trong `powerbi/measures.md`), thư viện measure, mapping;
   - mục **chỉ người làm được** (ảnh Power BI, ảnh Excel ToolPak, bài học nhóm…) thì để `[__]` và liệt kê theo người.

## Bước 3 – Sinh .pptx (`scripts/gen_pptx.py`, python-pptx trong `.venv`)
**Khổ và chữ**
- 16:9 (13,333 × 7,5 inch).
- Font **Arial** (an toàn với tiếng Việt, máy chiếu nào cũng có).
- Tiêu đề 28 pt, thân bài tối thiểu **18 pt**, bảng tối thiểu 14 pt, ghi nguồn 11 pt.

**Layout:** dùng template (xem phần Bối cảnh). Khi sinh slide:
- Ghi chú người nói vào **Notes** của slide.
- Mục lục dạng thẻ; trang chuyển phần cho 5 phần.
- Thẻ số và trước/sau vẽ giống file mẫu.

**Chống răng cưa** (quan trọng, áp dụng cho mọi hình)
- **Sơ đồ khối đơn giản** (≤ 12 khối, mũi tên, nhãn: quy trình, pipeline, phễu, kiến trúc tổng quan, data flow…): **vẽ bằng shape PowerPoint thật**, không dùng ảnh, để chữ sắc nét ở mọi mức phóng to và sửa tay được. Màu fact cam, dim xanh như quy ước.
- **Biểu đồ dữ liệu** (matplotlib/R): vẽ lại bằng `scripts/slide_fig.py` với kích thước bằng đúng ô đặt trên slide pptx, **300 dpi**, antialias. Chữ sau khi đặt ≥ 12 pt. Không bao giờ phóng ảnh to hơn kích thước gốc. Script kiểm tra: số pixel ÷ kích thước đặt (inch) phải ≥ 250 ppi.
- **Bảng:** bảng PowerPoint thật (dòng nhấn tô màu), không dùng ảnh bảng.
- **Ảnh chụp** (Power BI, Spark UI, terminal…): đặt không vượt quá độ phân giải gốc. Ảnh quá nhỏ thì liệt kê để chụp lại, không phóng.
- **Hình số thứ tự và chú thích** dưới mỗi hình ("Hình 3.4. …"). Mỗi biểu đồ có 1–2 câu nhận xét (thanh kết luận tính là một câu).

**Thứ tự và phụ lục**
- Đi theo `khung.yaml`.
- Mục lục dạng thẻ ở đầu.
- Trang chuyển phần cho 5 phần.
- Phụ lục sau trang Cảm ơn.

**Kết quả**
- `slides-pptx/Olist_Nhom19.pptx` (không commit file `.pptx` nếu nặng hơn 20 MB; ghi đường dẫn vào handoff).

## Bước 4 – Kiểm tra (bắt buộc)
1. **`scripts/kiem_tra_pptx.py`:**
   - mọi slide có tiêu đề ≤ 65 ký tự;
   - không có chữ < 18 pt ở thân bài (bảng < 14 pt);
   - không có shape nào ra ngoài slide hay chồng lên footer hoặc thanh tiêu đề;
   - ước lượng tràn chữ theo số dòng × cỡ chữ;
   - mọi ảnh ≥ 250 ppi tại kích thước đặt;
   - không còn `{MA}` chưa thay;
   - đếm `[__]` theo người;
   - tổng giờ theo công thức (Nói kỹ 30 s, Vừa 12 s, Lướt 4 s, demo khoảng 120 s) nằm trong **30–35 phút** (phụ lục không tính).
2. **Xem bằng mắt:** nếu máy có LibreOffice (`soffice`) thì xuất PDF → PNG, ghép ảnh xem trước, rồi mở từng ảnh để kiểm tràn chữ, chữ răng cưa, bố cục. Nếu không có thì **dừng và báo Phú**, không tự cài phần mềm. Chỉ ghi lại danh sách trang cần Phú mở PowerPoint kiểm tra.
3. Đối chiếu checklist mục 6 của md: bảng có / thiếu, kèm số slide.

## Kết thúc
- Commit (không commit `attach/`), merge, push.
- Handoff: `handoff/2026-11-26-P13-pptx.md`.

Báo lại cho Phú:
- số slide theo phần và theo mức (Nói kỹ / Vừa / Lướt), tổng phút;
- danh sách slide còn `[__]` theo người, và chỗ số liệu thành viên lệch số liệu chốt;
- kết quả kiểm tra;
- 6–8 ảnh xem trước tiêu biểu: bìa, chuyển phần, sơ đồ shape, biểu đồ, bảng, ảnh dashboard;
- những chỗ khung md mâu thuẫn với cách của nhóm và đã xử lý thế nào.
