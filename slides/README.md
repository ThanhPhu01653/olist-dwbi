# Bộ slide Beamer (theme HUST)

Bộ slide 16:9 theo theme HUST Beamer (Đại học Bách khoa Hà Nội, logo Khoa Toán - Tin): **113 slide nội dung xếp lại theo barem + 7 slide khung mở rộng + slide dự phòng** (dàn bài và lời thoại ở [`slide-script.md`](slide-script.md)). Trong 133 trang PDF có 123 trang chính (gồm bìa, mục lục, 7 trang chuyển mục, 114 slide) và 10 trang dự phòng đặt sau slide kết luận, **không tính vào thanh tiến trình và số trang**.

> **Sau P8 (13/11/2026)** các slide được xếp lại theo barem: 00 Mở đầu · 01 Khảo sát (2.1–2.5) · 02 Phân tích và thiết kế (3.1–3.5) · 03 Dashboard và bài học (4) · 04 Mở rộng (5, khung) · 05 Tổng kết (6) · 99 Dự phòng. Mỗi slide hiện **nhãn mục barem** ở góc trên bên phải (lệnh `\muc{2.4 · Dữ liệu nguồn}` đặt ngay sau `\begin{frame}`), và theme hiện tên phần ở thanh đầu trang. Số `[Sxx]` trong ghi chú giữ nguyên số cũ. **Không chạy `scripts/gen_beamer.py`** (script sinh theo cấu trúc cũ và sẽ ghi đè các file đã xếp lại); sửa trực tiếp `sections/*.tex` và `slide-script.md`.

## 1. Cấu trúc
```
slides/
  main.tex            cấu hình theme, thông tin nhóm (mục 3), bìa, mục lục, thứ tự các phần
  slides-notes.tex    cùng nội dung, nhưng mỗi slide kèm trang ghi chú người nói bên phải
  .latexmkrc          LuaLaTeX + đường dẫn theme (hust-theme/)
  sections/           00-mo-dau, 01-khao-sat, 02-phan-tich-thiet-ke, 03-dashboard, 04-mo-rong, 05-tong-ket (xếp theo barem), 99-du-phong (dự phòng B01-B10 + slide lý thuyết)
  figures/            hình dùng trong slide (bản sao từ figures/ ở gốc repo, để gói Overleaf tự chứa)
  hust-theme/         theme HUST Beamer 2.1.0 (đã bỏ thư mục references/ và các file PDF/PPTX lớn)
  slide-script.md     dàn bài: mỗi slide có tiêu đề (câu kết luận có số), nội dung, hình, ghi chú người nói
```
Mỗi slide là một `frame`: tiêu đề là câu kết luận có số, 1–3 dòng nội dung, hình hoặc bảng, và `\note{...}` chứa ghi chú người nói (có số slide `[Sxx]` ở đầu để đối chiếu với `slide-script.md`).

## 2. Biên dịch
- **Bắt buộc dùng LuaLaTeX** (theme dùng `fontspec`, font Lato, TikZ). Trong thư mục `slides/`:
  ```powershell
  latexmk -lualatex main.tex            # slides: main.pdf
  latexmk -lualatex slides-notes.tex    # có ghi chú người nói: slides-notes.pdf (trang rộng gấp đôi, ghi chú bên phải)
  ```
  `.latexmkrc` tự thêm `hust-theme/` vào `TEXINPUTS`; không cần cài theme vào hệ thống. Không dùng BibTeX/Biber (slide không có mục tài liệu tham khảo riêng).
- Đã biên dịch thành công trên TeX Live 2025 (LuaHBTeX 1.22). Một số cảnh báo `Overfull \vbox` nhỏ còn ở vài slide có hình cao; không ảnh hưởng nội dung.
- **Overfull / hình tràn khung**: mọi hình dùng `\anh[chiều cao tối đa]{file}` (giữ tỉ lệ, không vượt khung); bảng dùng `adjustbox` (tự thu nhỏ theo chiều rộng và chiều cao).

## 3. Sửa thông tin nhóm, tên thành viên, giảng viên
Mở `main.tex`, sửa khối **THÔNG TIN CẦN SỬA** ở đầu file:
```latex
\newcommand{\TenNhom}{[TÊN NHÓM]}
\newcommand{\ThanhVienA}{[Họ tên 1 -- MSSV]}   % ... đến \ThanhVienD
\newcommand{\GiangVien}{[Họ tên giảng viên]}
```
Các giá trị này xuất hiện ở bìa, chân trang và slide cảm ơn. Cần thêm thành viên thứ năm: thêm `\newcommand{\ThanhVienE}{...}` và thêm `\ThanhVienE` vào dòng `\author{...}` bên dưới. Tên môn và đề tài nằm ở `\title{...}`.

## 4. Thay ảnh chụp dashboard
Các slide cần ảnh dashboard hiện là **khung đỏ trống ghi "CHÈN ẢNH CHỤP DB1 … DB4"** (slide S93–S104, S145–S147 và vài slide khác). Cách thay:
1. Xuất ảnh từ Power BI (File → Export → hoặc chụp màn hình trang dashboard, nên PNG 16:9) và đặt vào `slides/figures/`, ví dụ `dashboard_D1.png`.
2. Mở file phần tương ứng trong `sections/` (ví dụ `03-dashboard.tex`), tìm đoạn `\khungchen{CHÈN ẢNH CHỤP DB1 trang 1}` và thay bằng:
   ```latex
   \begin{center}\anh[0.74\textheight]{dashboard_D1.png}\end{center}
   ```
3. Tìm `CHÈN` trong thư mục `sections/` để thấy mọi chỗ còn lại (ảnh dashboard, sơ đồ vẽ bằng draw.io, bảng cần chèn). Các slide gắn nhãn **[nhóm xác nhận]** (chữ đỏ ở góc dưới phải) cần kiểm tra lại số liệu hoặc nội dung trước khi trình bày; xóa lệnh `\canxacnhan` sau khi xác nhận.

## 5. Sửa nội dung slide
- **Sửa trực tiếp** file trong `sections/` nếu chỉ chỉnh vài chữ.
- **Hoặc sửa `slide-script.md` rồi sinh lại** các file phần: `python scripts/gen_beamer.py` (ghi đè toàn bộ `sections/*.tex`, vì vậy chỉ dùng cách này nếu chưa sửa tay trong `sections/`; số liệu bảng lấy từ `report/tables/`, chạy `python scripts/export_latex.py` trước nếu dữ liệu đổi).
- Hình mới đặt vào `slides/figures/` và dùng `\anh[0.74\textheight]{ten-file.png}`. Slide dự phòng B01–B10 nằm ở `sections/99-du-phong.tex` (câu hỏi đáp ở `huong-dan/04-cau-hoi-van-dap.md`).

## 6. Overleaf
1. Chạy `python scripts/make_slides_zip.py` ở gốc repo → `slides_overleaf.zip` (gồm theme; **không commit**, đã có trong `.gitignore`).
2. Overleaf → **New Project → Upload Project** → chọn file zip.
3. **Menu → Compiler = LuaLaTeX**; *Main document* = `main.tex` (đổi thành `slides-notes.tex` để xuất bản có ghi chú).
4. Biên dịch (lần đầu khoảng 1–2 phút do nhiều hình). Thay tên thành viên và ảnh dashboard theo mục 3 và 4.

## 7. Ghi chú kỹ thuật
- Theme định nghĩa lại `\note` thành ghi chú chân trang; `main.tex` khôi phục `\note` thành **ghi chú người nói của Beamer** (`\let\note\beamer@orig@note`). Ghi chú chân trang của theme vẫn dùng được qua `\hustnote{}{}`.
- Tiêu đề slide dài hơn một dòng bị theme cắt; vì vậy cỡ chữ tiêu đề đặt `\small` (`\setbeamerfont{frametitle}{size=\small}`). Tiêu đề không nên chứa `\texttt` hoặc `\_` (dùng `\symbol{95}` nếu cần dấu gạch dưới).
- Theme chỉ tải `hust-core`, các subtheme và `fami-shield.png`; không nạp `hust-setup.tex` (cần `minted` và `-shell-escape`), nên slide chạy được trên Overleaf không cần cấu hình thêm.
