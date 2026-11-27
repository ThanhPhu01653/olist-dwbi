# P12g – Zip slide tải lên Overleaf được và biên dịch kịp

Làm trên nhánh `phase/P12g`. Xong thì merge vào `main` và push. Không sửa nội dung slide, không sửa `huong-dan/`.

Trước khi làm: commit riêng `huong-dan/dashboards/D8.md` (Phú đã duyệt: D8 một trang).

## Bối cảnh

Nhóm không tải được `slides_overleaf.zip` lên Overleaf. Giới hạn của Overleaf (docs.overleaf.com, mục Plan limits và Uploading a project):
- **mỗi lần tải lên tối đa 180 file**, phần thừa bị bỏ;
- 7 MB nội dung sửa được; 50 MB mỗi file;
- **thời gian biên dịch của gói Free là 10 giây.**

Zip hiện tại:
- có **213 file**: `figures/` 153 file, trong đó nhiều hình cũ đã được thay bằng `figures/slide/`; `hust-theme/` 41 file; file rác ở gốc như `_sau_p12d.json`, `_truoc_p12d.json`, `QUY-TAC-TRINH-BAY.md`;
- **cả bộ 276 trang bằng LuaLaTeX** chắc chắn không biên dịch kịp 10 giây.

## Việc cần làm (`scripts/make_slides_zip.py`)

### 1. Zip đầy đủ (`slides_overleaf.zip`)
- Chỉ đưa vào những hình **thật sự được dùng**: quét `\includegraphics`, `\HinhLon`, `\AnhChup`, `AnhKhoanh`, `\HinhChu` và các macro hình khác trong `main.tex` và `sections/*.tex`, kể cả `99-du-phong.tex`.
- Bỏ: file `.json`, `.md`, `_xem_truoc/`, `slides/mau/`, README và `refs.bib` của theme (nếu theme không cần).
- Script **dừng và báo lỗi nếu quá 175 file**. In ra số file theo thư mục.

### 2. Zip theo người (`slides_overleaf_nguoi1.zip` … `nguoi4.zip`, `slides_overleaf_phu.zip`)
Mỗi zip chỉ có:
- theme, `bocuc.sty`, `hust-override.sty`;
- file khung của cả bộ, đổi tên thành `khung.tex`;
- file section của người đó;
- hình mà các section đó dùng.

`main.tex` trong zip người là file bọc kiểu `thu-mot-phan.tex`: đặt sẵn phần của người đó rồi `\input{khung.tex}`, để Overleaf mở là biên dịch đúng phần, không cần đổi Main document.

Phân file theo người, theo bảng khung chờ ở handoff P12:

| Người | File |
| --- | --- |
| Người 1 | `01a` |
| Người 2 | `00b`, `01b`, `02a` |
| Người 3 | `02b` |
| Người 4 | `03`, `05` |
| Phú | `00`, `04` |

`99-du-phong.tex` chỉ thêm vào zip của người có frame trong đó **nếu** biên dịch vẫn kịp. Nếu cơ chế `\CHIPHAN` chỉ nhận một file thì sửa để nhận danh sách.

### 3. Thời gian biên dịch
- Đo trên máy (`lualatex` một lượt, cache font đã có) thời gian từng zip người. Ghi vào handoff.
- Mục tiêu: **dưới khoảng 6 giây** để còn dư cho Overleaf (máy Overleaf thường chậm hơn).
- Nếu quá thì thêm công tắc nháp trong file bọc, ví dụ `\def\NHAP{}`, bật mặc định trong zip người:
  - `graphicx` ở chế độ `draft` (hình thành khung, không nạp ảnh);
  - bỏ trang tiêu đề, mục lục, trang chuyển phần.

  Ghi rõ trong comment đầu file: "muốn xem hình thật thì xoá dòng `\def\NHAP{}`; có thể quá 10 giây trên Overleaf Free".
- Thời gian biên dịch phụ thuộc gói của người tạo project, nên mỗi người tự tạo project từ zip của mình.

### 4. Ghép lại
`scripts/ghep_tex_nop.py` (hoặc thêm vào script đang có): nhận lại file section từ zip người, đặt trong `tex-nop/<nguoi>/`, rồi chép vào `slides/sections/` (chỉ file section và hình mới). In ra file nào thay đổi. Chưa chạy, chỉ chuẩn bị.

### 5. Biên dịch được ở mọi nơi, không chỉ Overleaf
Một số bạn sẽ biên dịch trên máy bằng MiKTeX + TeXstudio, không qua `latexmk`, nên `.latexmkrc` (biến `TEXINPUTS` trỏ tới `hust-theme/`) không có tác dụng. Với mọi zip (đầy đủ và theo người):
- Đặt các file `.sty` và `.tex` của theme (không phải thư mục `assets/`) **ở gốc zip**, để `lualatex main.tex` chạy thẳng mà không cần `TEXINPUTS`. Sửa `\graphicspath` nếu cần.
- Dòng đầu của `main.tex` (cả file bọc lẫn `khung.tex`): `% !TeX program = lualatex`. TeXstudio và VS Code LaTeX Workshop đọc dòng này để tự chọn LuaLaTeX.
- Thử trong thư mục tạm, **không có** `.latexmkrc`: `lualatex main.tex` hai lượt, không lỗi.

## Kiểm tra
1. Mỗi zip: số file ≤ 175. Giải nén ra thư mục tạm, chạy `latexmk -lualatex main.tex`, không lỗi.
2. Zip đầy đủ vẫn biên dịch ra `main.pdf` như hiện tại (276 trang).
3. Tạo lại `slides_overleaf.zip`, các zip người, `report_overleaf.zip`. Báo cáo: kiểm tra số file ≤ 175; quá thì lọc hình như mục 1.

## Kết thúc
- Commit (zip không commit), merge, push.
- Handoff: `handoff/2026-11-25-P12g-zip.md`.

Báo lại cho Phú:
- số file từng zip;
- thời gian biên dịch đo được từng zip, có hay không có chế độ nháp;
- hướng dẫn 4 bước để Phú gửi nhóm: tải zip của mình → Overleaf New Project → Upload Project → Recompile; nộp lại thì Menu → Download → Source.
