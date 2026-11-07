# Báo cáo LaTeX – khung để nhóm viết tiếp

Khung báo cáo bài tập lớn **MI4214 – Kho dữ liệu và Kinh doanh thông minh**, biên dịch bằng **XeLaTeX** (class `report`, 12pt, A4, tiếng Việt, font Times New Roman; nếu máy không có thì tự dùng TeX Gyre Termes). Đã biên dịch thử thành công trên máy Phú (TeX Live 2025, `latexmk -xelatex main.tex`): **88 trang PDF** (khung, chưa tính phần nhóm viết thêm), không lỗi, không tham chiếu thiếu.

## 1. Cấu trúc
```
report/
  main.tex            thứ tự các phần của báo cáo (đừng đổi thứ tự dàn ý)
  preamble.tex        gói, font, lề, lệnh \hinh, \khunganh, \code, kiểu code
  refs.bib            tài liệu tham khảo (BibTeX)
  .latexmkrc          ép Overleaf / latexmk dùng XeLaTeX
  chapters/           MỖI MỤC MỘT FILE (nhóm sửa trực tiếp các file này)
  tables/             bảng số liệu SINH TỰ ĐỘNG từ database (đừng sửa tay)
  code/               đoạn SQL cắt từ sql/ (sinh tự động)
  figures/            hình (bản sao của figures/ ở gốc repo, để zip Overleaf tự chứa)
```
Các file trong `chapters/`:

| File | Mục báo cáo | Trạng thái |
| --- | --- | --- |
| `00-bia`, `00-loi-mo-dau`, `00-danh-gia-thanh-vien`, `00-tu-danh-gia`, `00-viet-tat` | Bìa, lời mở đầu, bảng đánh giá thành viên (5 tiêu chí, thang 1–5, ≥ 4 bậc điểm, cả nhóm ký), tự đánh giá báo cáo, từ viết tắt | khung + `\todo` |
| `01-tong-quan-dw`, `02-tong-quan-bi` | Chương 1, Chương 2 | **chỉ gạch đầu dòng ý chính + trích dẫn gợi ý**, nhóm tự viết (Ch.1 có ý so sánh MOLAP/ROLAP/HOLAP và lý do chọn ROLAP) |
| `3-1-gioi-thieu` … `3-5-2-dia-ly` | Chương 3 (3.1; 3.2.1–3.2.4; 3.3.1–3.3.5; 3.4.1–3.4.5; 3.5.1–3.5.2) | **đoạn nháp có sẵn** (từ `handoff/` và `huong-dan/`), hình và bảng đã chèn; phần nhóm phải viết/xác nhận có `\todo{...}` |
| `04-ket-luan` | Kết luận và bài học | nháp + `\todo` |
| `phu-luc-dax`, `phu-luc-sql` (+ `tables/mapping`) | Phụ lục A (DAX), B (SQL tiêu biểu), C (mapping) | sinh tự động |

**`\todo{...}`** (gói `todonotes`) hiện thành khung **cam** ngay trong văn bản: là việc nhóm phải làm (viết, xác nhận số, chèn ảnh chụp dashboard…). Xoá lệnh `\todo` khi đã xong. Bỏ dấu `%` ở dòng `\listoftodos` trong `main.tex` để xem danh sách tất cả việc còn lại. Trước khi nộp: tìm `\todo` phải ra 0 kết quả.

## 2. Biên dịch
- **Trên máy** (cần TeX Live / MiKTeX có XeLaTeX và gói `babel-vietnamese`, `todonotes`, `listings`, `booktabs`, `longtable`): trong thư mục `report/` chạy `latexmk -xelatex main.tex` (file `.latexmkrc` đã chọn XeLaTeX nên `latexmk main.tex` cũng được). Kết quả `main.pdf`. Dọn file tạm: `latexmk -C`.
- **Trên Overleaf** (khuyến nghị cho cả nhóm): xem mục 3.
- Font: nếu máy có *Times New Roman* thì dùng, nếu không (Overleaf) tự chuyển sang *TeX Gyre Termes* (tương đương). Đổi trong `preamble.tex`.

## 3. Overleaf: tạo project và làm việc nhóm
1. Thành viên giữ project Overleaf (ví dụ trưởng nhóm) chạy `python scripts/make_overleaf_zip.py` ở gốc repo → ra `report_overleaf.zip` (không commit, đã có trong `.gitignore`).
2. Trên Overleaf: **New Project → Upload Project** → chọn `report_overleaf.zip`.
3. **Menu → Compiler = XeLaTeX**, *Main document* = `main.tex`. Biên dịch.
4. Mời thành viên (nút *Share*) nếu dùng tài khoản có cho phép cộng tác; hoặc làm theo cách 5.

**Cách nhiều người cùng viết mà chỉ một người giữ project Overleaf** (không cần Overleaf trả phí):
- Mỗi người nhận **mục của mình** (ví dụ `3-3-4-thiet-ke-kho.tex`, `3-4-5-dashboard.tex`) và chỉ sửa các file đó trong bản sao `report/chapters/` ở máy mình (hoặc gửi nội dung mục). Không ai sửa `main.tex`, `preamble.tex`, `tables/`.
- Gửi lại **đúng các file `.tex` đã sửa** (qua nhóm chat / Git) cho người giữ project. Hình mới cho vào `figures/` với tên đúng quy ước (`3-x-y_ten.png`) và gửi kèm.
- Người giữ project vào Overleaf: **mở file tương ứng → chọn hết → dán nội dung mới** (hoặc nút *Upload* thả file đè lên cùng tên), biên dịch kiểm tra, rồi nhắn lại nếu có lỗi cú pháp.
- Quy ước tránh xung đột: mỗi người **một mục một file**; không đổi tên nhãn `\label`; thêm hình bằng lệnh `\hinh{tên-file.png}{Chú thích}{fig:nhan}{0.9}`; thêm bảng số liệu mới bằng cách nhờ người chạy code thêm vào `scripts/export_latex.py`.
- Cách tốt hơn nếu nhóm quen Git: sửa trong repo GitHub (nhánh riêng cho từng người), gộp bằng pull request, rồi người giữ project tạo lại `report_overleaf.zip`.

## 4. Cập nhật số liệu khi dữ liệu đổi
Số liệu trong `tables/` luôn sinh từ database để khớp kho:
```powershell
python scripts/export_latex.py        # ghi lại report/tables/*.tex và report/code/*.sql từ olist_dw
cd report; latexmk -xelatex main.tex
```
Hình mới: chép từ `figures/` ở gốc repo vào `report/figures/` (hoặc chạy lại `scripts/bootstrap_report.py --force` **chỉ khi muốn dựng lại khung từ đầu: lệnh này ghi đè chữ của nhóm**).
Các đoạn nháp ở Chương 3 là **ảnh chụp tại thời điểm tạo khung**; nếu số liệu kho đổi thì sửa lại các con số viết tay trong đoạn văn (bảng trong `tables/` tự cập nhật).

## 5. Việc cần làm trước khi nộp (checklist)
- [ ] Điền bìa (giảng viên, lớp/nhóm, thành viên, logo) và xác nhận tên viện.
- [ ] Viết Chương 1, Chương 2 (khung ý chính có sẵn; trích dẫn trong `refs.bib` đánh dấu \[GỢI Ý\] cần đọc và kiểm tra).
- [ ] Giải quyết mọi `\todo` (đặc biệt: Business Model Canvas, BPMN, ERD có gạch chân, sơ đồ kiến trúc có logo công nghệ, ảnh chụp dashboard D1–D7, nhận xét dashboard).
- [ ] Vẽ lại các hình nháp bằng draw.io (hình nháp tự động trong `figures/`: `3-2-*`, `3-3-4_*`, `3-4-1_pipeline`); thay file trong `report/figures/` (giữ nguyên tên file).
- [ ] Bảng đánh giá thành viên: trưởng nhóm điền điểm (≥ 4 bậc điểm), cả nhóm ký.
- [ ] Điền bảng "Tự đánh giá báo cáo".
- [ ] Soát chính tả, số trang, mục lục / danh mục hình / bảng; font Times New Roman 12, căn lề hai bên.
- [ ] Tài liệu tham khảo: chỉ giữ nguồn thật sự đã đọc; mọi `\cite` đều có trong `refs.bib`.

## 6. Ghi chú kỹ thuật
- Mọi số liệu trong `tables/` lấy từ truy vấn thật trên `olist_dw` (trạng thái cuối); bảng benchmark và dựng lại từ đầu được đọc từ `handoff/benchmark.md` và `handoff/rebuild-report.md`.
- Lệnh `\hinh{file}{caption}{label}{width}` chèn hình trong `figures/`; `\khunganh{mô tả}{caption}` tạo khung trống chờ ảnh chụp dashboard; `\code{...}` cho tên bảng/cột.
- Đã biên dịch thành công với `latexmk -xelatex` (2 lượt + BibTeX). Cảnh báo `Overfull \hbox` còn một số ở các bảng rộng; nhóm chỉnh khi hoàn thiện.
