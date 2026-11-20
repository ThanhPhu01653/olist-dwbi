# P11 – Trình bày lại slide cho máy chiếu

Đọc trước:
- `slides/QUY-TAC-TRINH-BAY.md` (quy tắc R1–R9 và 6 mẫu slide);
- `slides/bocuc.sty` (macro bố cục);
- `slides/mau/mau-bo-cuc.tex` (8 frame mẫu đã biên dịch thử);
- `slides/mau/truoc-sau.png` (bên trái là slide hiện tại, bên phải là cùng nội dung theo mẫu mới).

Làm trên nhánh `phase/P11-slide`. Xong thì merge vào `main` và push.

## Bối cảnh

Slide chương 5 hiện khó nhìn khi chiếu:
- hai ảnh trên một trang;
- ảnh nằm trong cột hẹp;
- bảng `\scriptsize`;
- sơ đồ kiến trúc thu nhỏ đến không đọc được;
- tiêu đề phần 5.2 dài nên bị theme cắt.

Việc này **chỉ đổi cách trình bày**, không đổi số liệu và không thêm nhận định mới. Chữ bỏ khỏi slide thì chuyển vào `\note{}`, không xoá.

## Phạm vi

- **Được sửa** (file của Phú): `slides/sections/00-mo-dau.tex`, `04-mo-rong.tex`, `05-tong-ket.tex`.
- **KHÔNG sửa** file của thành viên khác (`00b`, `01a`, `01b`, `02a`, `02b`, `03`): họ đang sửa trên Overleaf. Chỉ chạy kiểm tra và báo lại kết quả cho các file này (bước 5).
- **`99-du-phong.tex`** là slide dự phòng, chỉ dùng khi bị hỏi: chỉ sửa lỗi R2, R3, R4.

## Việc cần làm

### 1. Cài đặt
- `slides/bocuc.sty` đã có sẵn. Thêm `\usepackage{bocuc}` vào `slides/main.tex`, ngay sau dòng `\usetikzlibrary{...}`.
- Thêm `bocuc.sty` vào `scripts/make_slides_zip.py` (zip Overleaf phải có file này). Không đưa `slides/mau/` vào zip.
- Thêm `slides/_xem_truoc/` vào `.gitignore`.
- Thêm vào `CLAUDE.md`, mục quy ước: "Slide: theo `slides/QUY-TAC-TRINH-BAY.md`; trước khi commit slide chạy `python scripts/kiem_tra_slide.py --strict` (0 LỖI) và xem ảnh `--anh`."
- Cài thư viện để xuất ảnh: `pip install pymupdf` (trong `.venv`).

### 2. Ảnh chụp và hình
- **Ảnh chụp:** cắt bằng `scripts/cat_anh.py` từ `figures/human_takes/` hoặc ảnh đang có. Ghi ra file mới đuôi `_tc.png`, không sửa file gốc.
  - Spark UI: tách Streaming và Jobs thành 2 bước `\only`.
  - reconcile: cắt bỏ phần trống bên phải, khoanh dòng `RESULT` và dòng `GMV`.
  - dbt test: dùng ảnh nửa cuối, khoanh dòng `PASS=71`.
- **Sơ đồ `5-1_kien_truc_lakehouse` và `5-2_kien_truc_api`:** vẽ lại cho slide 16:9 theo mục 6 của quy tắc.
  - Một bản tổng quan, tối đa khoảng 12 khối, chữ to.
  - Nếu cần chi tiết: thêm 1–2 slide phóng to từng phần.
  - Giữ bản cũ cho báo cáo.
- **Biểu đồ `5-1_latency` và `5-2_*`:** sinh lại bằng chính script đã tạo ra chúng, với `figsize=(12,6)`, chữ trục tối thiểu 14, bỏ tiêu đề trong hình. Số liệu giữ nguyên.

### 3. Viết lại frame
- Với từng frame trong 3 file được sửa: chọn một trong 6 mẫu của mục 4 trong quy tắc, rồi viết lại.
  - Tiêu đề: câu kết luận có số, tối đa 80 ký tự.
  - Slide có hình hoặc bảng: thêm `\KetLuan{}` một dòng.
- Hai ảnh trên một trang: dùng `\only<1>` / `\only<2>`.
- Bảng quá 8 dòng: gom dòng (như ví dụ bảng topic CDC trong `mau-bo-cuc.tex`) hoặc tách.
- **Giữ cấu trúc chương 5:** 5.1 Lakehouse rồi 5.2 Thu thập API; mỗi phần theo kiến trúc → triển khai (mỗi bước một slide làm và một slide minh chứng) → kết quả.
- Số trang có thể tăng do tách slide. Mục tiêu: phần thuyết trình chương 5 khoảng 18–22 trang được nói. Các trang chi tiết dồn về cuối mỗi phần hoặc sang `99-du-phong.tex`.
- **Slide Superset:** giữ khung chờ, đổi sang mẫu B. Khi Phú có ảnh `5-1_superset_db1.png` thì chỉ cần thay tên file.

### 4. Kiểm tra (bắt buộc, lặp đến khi đạt)
1. Biên dịch: `latexmk -lualatex main.tex`. Không lỗi, không trang nào có `Overfull \vbox` ở 3 file được sửa.
2. `python scripts/kiem_tra_slide.py --strict slides/sections/00-mo-dau.tex slides/sections/04-mo-rong.tex slides/sections/05-tong-ket.tex` cho 0 LỖI. Mục NÊN còn lại phải có lý do.
3. `python scripts/kiem_tra_slide.py --anh slides/main.pdf <trang đầu>-<trang cuối>` cho các trang của 3 file. Mở **từng** ảnh `slides/_xem_truoc/trang-*.png` và kiểm:
   - tiêu đề không bị cắt;
   - chữ trong ảnh đọc được ở 1280 px;
   - thanh kết luận không chạm chân trang;
   - không có khoảng trống lớn một bên.
   Sửa xong thì xuất và xem lại.
4. Tạo lại `slides_overleaf.zip`.

### 5. Báo cáo cho các file của thành viên (không sửa)
- Chạy `kiem_tra_slide.py` trên `00b`, `01a`, `01b`, `02a`, `02b`, `03`.
- Ghi kết quả vào `handoff/2026-11-2x-P11-slide.md`: số LỖI và NÊN theo file, và 3 lỗi tiêu biểu mỗi file.
- Thêm vào `huong-dan/phan-viec/README.md` một mục ngắn "Trình bày slide", trỏ tới `slides/QUY-TAC-TRINH-BAY.md` và 6 mẫu. Giọng trung lập, không nêu tên ai.

## Kết thúc
- Commit (chỉ `git add` đúng file đã sửa), merge, push.

Báo lại cho Phú:
- số trang chương 5 trước và sau;
- kết quả kiểm tra (0 LỖI);
- danh sách hình đã vẽ lại hoặc cắt lại;
- bảng LỖI/NÊN của các file thành viên;
- ảnh `slides/_xem_truoc/ghep-*.png` của chương 5 để Phú xem.
