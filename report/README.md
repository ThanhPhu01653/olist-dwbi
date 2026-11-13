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
Các file trong `chapters/` (xếp theo **barem chấm điểm**; mỗi mục cấp 2 là một file; thứ tự chương: 1 Tổng quan lý thuyết · 2 Khảo sát · 3 Phân tích và thiết kế · 4 Dashboard và BI · 5 Mở rộng · 6 Kết luận):

| File | Mục báo cáo | Trạng thái |
| --- | --- | --- |
| `00-bia`, `00-loi-mo-dau`, `00-danh-gia-thanh-vien`, `00-tu-danh-gia`, `00-viet-tat` | Bìa, lời mở đầu, bảng đánh giá thành viên (5 tiêu chí, thang 1–5, ≥ 4 bậc điểm, cả nhóm ký), tự đánh giá báo cáo, từ viết tắt | khung + `\todo` |
| `01-tong-quan-ly-thuyet` | Chương 1 (gộp tổng quan DW và BI cũ; cần rút còn khoảng 10 trang) | **chỉ gạch đầu dòng ý chính + trích dẫn gợi ý**, nhóm tự viết (có ý so sánh MOLAP/ROLAP/HOLAP và lý do chọn ROLAP) |
| `2-1-nghiep-vu` | 2.1 Giới thiệu bài toán, quy trình nghiệp vụ | đoạn nháp + `\todo` |
| `2-2-yeu-cau` | 2.2 Yêu cầu phân tích | đoạn nháp + `\todo` |
| `2-3-kpi` | 2.3 KPI và cây phân tích | đoạn nháp + `\todo` |
| `2-4-du-lieu-nguon` | 2.4 Dữ liệu nguồn (quy mô, tần suất, taxonomy, data flow) | đoạn nháp + `\todo` |
| `2-5-erd-oltp` | 2.5 ERD OLTP, mapping sang OLAP | đoạn nháp + `\todo` |
| `3-1-kham-pha` | 3.1 Khám phá dữ liệu (gồm khoảng cách địa lý seller → khách) | đoạn nháp + `\todo` |
| `3-2-kien-truc` | 3.2 Kiến trúc kho dữ liệu | đoạn nháp + `\todo` |
| `3-3-etl` | 3.3 ETL (ODS, môi trường, làm sạch, đối soát, nạp tăng dần) | đoạn nháp + `\todo` |
| `3-4-chieu-khai-niem` | 3.4 Hệ thống chiều khái niệm (dimension) | đoạn nháp + `\todo` |
| `3-5-data-model` | 3.5 Data model OLAP (fact, vật lý, data mart, OLAP, hiệu năng) | đoạn nháp + `\todo` |
| `4-dashboard` | Chương 4: bốn dashboard DB1–DB4, thống kê, publish và QR, bài học | khung + nhận xét gợi ý + `\todo` |
| `5-1-lakehouse`, `5-2-thu-thap-api` | Chương 5: mở rộng (lakehouse; thu thập dữ liệu từ API) | khung `\todo`, do P10 và P9 điền |
| `06-ket-luan` | Chương 6: kết luận và bài học | nháp + `\todo` |
| `phu-luc-dax`, `phu-luc-sql` (+ `tables/mapping`) | Phụ lục A (DAX), B (SQL tiêu biểu), C (mapping) | sinh tự động |

Đổi tên file ở P8 (cũ → mới): `01-tong-quan-dw` + `02-tong-quan-bi` → `01-tong-quan-ly-thuyet`; `3-1-gioi-thieu` + `3-2-1-quy-trinh` → `2-1-nghiep-vu`; `3-2-2-yeu-cau` → `2-2-yeu-cau`; `3-3-5-kpi` → `2-3-kpi`; `3-2-3-he-thong-du-lieu` → `2-4-du-lieu-nguon`; `3-2-4-erd-oltp` → `2-5-erd-oltp`; `3-3-1-kham-pha` + `3-5-2-dia-ly` → `3-1-kham-pha`; `3-3-2-kien-truc` → `3-2-kien-truc`; `3-3-3-ods` + `3-4-1-moi-truong` + `3-4-2-staging-ods` + `3-4-3-doi-soat-tang-dan` → `3-3-etl`; `3-3-4-thiet-ke-kho` (phần dimension) → `3-4-chieu-khai-niem`; `3-3-4-thiet-ke-kho` (phần fact) + `3-4-4-mart-olap` + `3-5-1-hieu-nang` → `3-5-data-model`; `3-4-5-dashboard` → `4-dashboard`; `04-ket-luan` → `06-ket-luan`.

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
- Mỗi người nhận **mục của mình** (ví dụ `3-5-data-model.tex`, `4-dashboard.tex`) và chỉ sửa các file đó trong bản sao `report/chapters/` ở máy mình (hoặc gửi nội dung mục). Không ai sửa `main.tex`, `preamble.tex`, `tables/`.
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
- [ ] Giải quyết mọi `\todo` (đặc biệt: Business Model Canvas, BPMN, ERD có gạch chân, sơ đồ kiến trúc có logo công nghệ, ảnh chụp dashboard DB1–DB4, nhận xét dashboard).
- [ ] Vẽ lại các hình nháp bằng draw.io (hình nháp tự động trong `figures/`: `3-2-*`, `3-3-4_*`, `3-4-1_pipeline` (giữ nguyên tên file cũ khi vẽ lại)); thay file trong `report/figures/` (giữ nguyên tên file).
- [ ] Bảng đánh giá thành viên: trưởng nhóm điền điểm (≥ 4 bậc điểm), cả nhóm ký.
- [ ] Điền bảng "Tự đánh giá báo cáo".
- [ ] Soát chính tả, số trang, mục lục / danh mục hình / bảng; font Times New Roman 12, căn lề hai bên.
- [ ] Tài liệu tham khảo: chỉ giữ nguồn thật sự đã đọc; mọi `\cite` đều có trong `refs.bib`.

## 6. Ghi chú kỹ thuật
- Mọi số liệu trong `tables/` lấy từ truy vấn thật trên `olist_dw` (trạng thái cuối); bảng benchmark và dựng lại từ đầu được đọc từ `handoff/benchmark.md` và `handoff/rebuild-report.md`.
- Lệnh `\hinh{file}{caption}{label}{width}` chèn hình trong `figures/`; `\khunganh{mô tả}{caption}` tạo khung trống chờ ảnh chụp dashboard; `\code{...}` cho tên bảng/cột.
- Đã biên dịch thành công với `latexmk -xelatex` (2 lượt + BibTeX). Cảnh báo `Overfull \hbox` còn một số ở các bảng rộng; nhóm chỉnh khi hoàn thiện.
