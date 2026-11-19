# Phân việc và cách làm chung

Mỗi thành viên mở **một file** của mình (`Nguoi-1.md` … `Nguoi-4.md`) để biết cần làm gì, cần hiểu gì, dùng số liệu và hình nào, nộp gì và nộp ở đâu. File này là phần chung cho cả nhóm: phân công, cách dùng Drive, Power BI, slide Beamer trên Overleaf và draw.io.

## 1. Phân công

Nhóm làm hai giai đoạn:
- **Giai đoạn 1, trước thuyết trình:** làm slide, sơ đồ draw.io và dashboard.
- **Giai đoạn 2, sau thuyết trình:** viết báo cáo, dựa trên slide của chính mình.

| Người | Mục (báo cáo / slide) | draw.io | Dashboard | Thuyết trình |
| --- | --- | --- | --- | --- |
| [Người 1](Nguoi-1.md) | Ch.1 lý thuyết rút gọn (slide: tối đa 2 trang trong phần mở đầu) → 2.1 Nghiệp vụ → 2.2 Yêu cầu → 2.3 KPI và cây phân tích | 2 BPMN: `3-2-1_bpmn_don_hang.png`, `3-2-2_bpmn_thu_hut_seller.png` | DB1 Tổng quan và doanh thu | Khảo sát 2.1–2.3 |
| [Người 2](Nguoi-2.md) | 2.4 Dữ liệu nguồn → 2.5 ERD OLTP → 3.1 Khám phá dữ liệu | `2-4_data_taxonomy`, `2-4_data_flow_hien_trang`, `2-4_data_flow_de_xuat`, `2-5_erd_oltp_gach_chan`, `2-5_data_flow_oltp_olap` | DB2 Giao hàng và trải nghiệm khách | Khảo sát 2.4–2.5, Khám phá dữ liệu |
| [Người 3](Nguoi-3.md) | 3.2 Kiến trúc → 3.3 ETL → 3.4 Chiều khái niệm → 3.5 Data model | `3-2_kien_truc_cac_lop` (có logo), `3-3_etl_jobs`, `3-5_data_model_logic`, `3-5_data_model_vat_ly`, `3-5_data_mart` | DB3 Địa lý và phí vận chuyển | Kiến trúc, ETL, chiều khái niệm, data model |
| [Người 4](Nguoi-4.md) | Ch.4 Dashboard: bản đồ bộ dashboard, giới thiệu và demo 4 dashboard, QR; bài học tổng kết của cả nhóm | Bản đồ bộ dashboard | DB4 Thu hút và hiệu quả seller | Dashboard và bài học tổng kết |
| Phú | Mở đầu; Ch.5 Mở rộng (Lakehouse, thu thập API, D8, DB1 trên Superset); kết luận | Kiến trúc Lakehouse | File gốc, D8, ghép file tổng, publish | Mở đầu, mở rộng, kết luận |

Việc riêng thêm:
- Người 2: chạy Excel ToolPak trên `eda_sample.xlsx`, chụp ảnh đối chiếu với sheet `python_doi_chieu`.
- Người 3: chạy mã M trong `powerbi/power-query-vi-du.md`, chụp ảnh before/after.
- Người 4: gom bài học của cả nhóm và kiểm tra checklist của 4 dashboard.

**Mỗi file slide do một người phụ trách** (để khi ghép không ghi đè lên nhau):

| File slide (`slides/sections/`) | Người phụ trách | Mục |
| --- | --- | --- |
| `00-mo-dau.tex` | Phú | Mở đầu |
| `00b-ly-thuyet-rut-gon.tex` | Người 1 | Ch.1 lý thuyết rút gọn (2 frame) |
| `01a-nghiep-vu-yeu-cau.tex` | Người 1 | 2.1–2.3 |
| `01b-du-lieu-nguon-erd.tex` | Người 2 | 2.4–2.5 |
| `02a-kham-pha.tex` | Người 2 | 3.1 |
| `02b-kien-truc-etl-model.tex` | Người 3 | 3.2–3.5 |
| `03-dashboard.tex` | Người 4 | 4 và bài học |
| `04-mo-rong.tex`, `05-tong-ket.tex`, `99-du-phong.tex` | Phú | 5, 6, dự phòng |

Báo cáo (`report/chapters/`) đã chia theo file cho từng người: `01-tong-quan-ly-thuyet`, `2-1`, `2-2`, `2-3` (Người 1); `2-4`, `2-5`, `3-1` (Người 2); `3-2`, `3-3`, `3-4`, `3-5` (Người 3); `4-dashboard` (Người 4); `5-1`, `5-2`, `06-ket-luan`, `00-*` và phụ lục (Phú).


## 2. Drive và quy tắc đặt tên

| Thư mục | Nội dung |
| --- | --- |
| `01_pBI_data` | 45 file CSV cho Power BI (không đổi tên file); `olist_geolocation_dataset.csv` (file nguồn Kaggle, chỉ Người 3 cần) |
| `02_Dashboard` | `olist_base.pbix` (file gốc); file riêng `DBx_<tên>.pbix`; ảnh `4_DBx_<mô-tả>.png` |
| `03_drawio` | file `.drawio` và PNG xuất ra |
| `04_Docs` | `slides_overleaf.zip` (bộ slide để tạo project Overleaf); `slides.pdf` (bản biên dịch hiện tại, để xem); `report_overleaf.zip` (báo cáo, dùng ở giai đoạn 2); `tex-nop/` (nộp file `.tex`, hình mới ở `tex-nop/figures/`); `tham-khao/` (slide nhóm 6) |
| `De_Xuat_Lam` | hướng dẫn chung (`00-Chung.pdf`) và hướng dẫn riêng của từng người (`Nguoi-1.pdf` … `Nguoi-4.pdf`) |

Quy tắc đặt tên:
- File Power BI: `DB1_tong-quan.pbix`, `DB2_giao-hang.pbix`, `DB3_dia-ly.pbix`, `DB4_thu-hut-seller.pbix` (giữ nguyên file gốc `olist_base.pbix`).
- Ảnh dashboard: `4_DBx_<mô-tả>.png`, mô tả không dấu, nối bằng dấu gạch dưới, ví dụ `4_DB1_trang1_tong_quan.png`.
- Sơ đồ: giữ **đúng tên file cũ** của PNG (ví dụ `2-5_erd_oltp_gach_chan.png`), vì slide và báo cáo đã trỏ tới tên đó.
- File `.tex` nộp: giữ tên file như trong repo; hình mới đặt trong thư mục con `figures/` cùng chỗ (mục 4).
- Khi sửa lại một file đã nộp: ghi đè cùng tên và báo lên nhóm; không thêm hậu tố `_v2`, `_final`.

## 3. Power BI

Dữ liệu (45 file CSV ở `01_pBI_data`) lấy từ kho ở trạng thái cuối: 99.441 đơn, GMV 13.494.400,74 BRL. Mọi người dựng trên **cùng một mô hình** (46 bảng, 33 quan hệ, 76 measure, gồm cả các bảng của dashboard D8 ở chương 5), nên số liệu phải giống nhau giữa bốn dashboard.

1. **Tải về và mở file gốc.** Tải thư mục `01_pBI_data` (45 file CSV) về một thư mục cố định, ví dụ `D:\Olist\01_pBI_data`; tải `olist_base.pbix` ở `02_Dashboard` về `D:\Olist`. Mở `olist_base.pbix` bằng Power BI Desktop (chỉ có cho Windows).
2. **Lưu thành file của mình trước khi dựng:** *File → Save as* → `DBx_<tên>.pbix` (mục 2). Giữ nguyên `olist_base.pbix` để bốn dashboard dùng chung một mô hình và ghép lại được.
3. **Đổi `DataFolder` khi cần Refresh.** *Home → Transform data → Edit parameters* → `DataFolder` = đường dẫn thư mục chứa các file CSV trên máy, không có dấu `\` ở cuối (ví dụ `D:\Olist\01_pBI_data`) → *OK*, rồi *Home → Refresh*. Nếu báo `DataSource.NotFound`: đường dẫn sai hoặc còn dấu `\` ở cuối. Hướng dẫn đầy đủ và bảng lỗi thường gặp: `powerbi/olist_base/README.md` mục 3, 7 và `powerbi/model.md` mục 10–11.
4. **Lấy measure trong thư mục measure.** Measure nằm trong bảng `_Measures`, xếp theo thư mục hiển thị: `DB1 Tổng quan và doanh thu`, `DB2 Giao hàng và trải nghiệm khách`, `DB3 Địa lý và phí vận chuyển`, `DB4 Thu hút và hiệu quả seller`, `Cảnh báo màu` (các measure `Color …` cho định dạng có điều kiện), `Giám sát ETL`. Kéo measure vào visual; **không viết lại measure**. Định nghĩa DAX: `powerbi/measures.md`.
5. **Dựng theo `huong-dan/dashboards/DBx.md`** (bố cục từng trang, slicer, định dạng có điều kiện, checklist ở mục 10) và checklist chung ở `huong-dan/dashboards/README.md`. Bộ lọc trang: `dim_date[InWindow] = TRUE` (2017-01 → 2018-08).
6. **Đối chiếu số với bảng giá trị kỳ vọng** (mục 9 của `DBx.md`, và `powerbi/measures.md` mục 7): đặt measure vào thẻ (card), so với cột "Cửa sổ 2017-01 → 2018-08" khi bật `InWindow`, cột "Toàn bộ dữ liệu" khi bỏ lọc. Thẻ hiển thị rút gọn (GMV `13.5M`, Orders `98.2K`) nên so theo số làm tròn. Số lệch thì kiểm tra bộ lọc và quan hệ trước khi sửa measure.
7. **Chụp ảnh.** Mở trang ở chế độ *Fit to page*, ẩn khung *Filters* nếu không cần, chụp toàn trang bằng Snipping Tool (Win+Shift+S) rồi lưu PNG. Tên `4_DBx_<mô-tả>.png`, đưa lên `02_Dashboard`. Mỗi ảnh gửi kèm 3–5 câu nhận xét có số (xem mục "Dashboard" trong file của từng người).

## 4. Slide Beamer trên Overleaf

**Cách làm việc.**
1. Tải `slides_overleaf.zip` ở `04_Docs`. Trên Overleaf: *New Project → Upload Project* → chọn zip.
2. *Menu → Compiler = LuaLaTeX*; main document là `main.tex`. Bộ đầy đủ khoảng 167 trang nên biên dịch lâu: khi đang sửa, đặt *Main document* = `thu-mot-phan.tex` (chỉ biên dịch một file; sửa dòng `\def\CHIPHAN{sections/...}` thành file của mình, không có đuôi `.tex`). Khi xong đổi lại `main.tex`. Trên máy: `latexmk -lualatex thu-mot-phan.tex`.
3. **Chỉ sửa file `.tex` của mình** trong `sections/` (bảng ở mục 1). Không sửa `main.tex`, `hust-theme/` hay file của người khác.
4. Nộp: đưa file `.tex` đã sửa cùng hình mới vào `04_Docs/tex-nop/` (file `.tex` ở `tex-nop/`, hình mới ở `tex-nop/figures/`) và báo lên nhóm.

**Mẫu frame.** Mỗi slide là một `frame`: tiêu đề là câu kết luận có số, nhãn mục barem ngay sau `\begin{frame}`, nội dung 1–3 dòng, một hình hoặc bảng, ghi chú người nói trong `\note`.

Frame thường:
```latex
\begin{frame}{Giao trễ làm điểm review rơi từ 4,29 xuống 1,70}
\muc{3.1 · Khám phá dữ liệu}
\begin{itemize}
  \item Đơn giao sớm: 4,29 điểm; đơn trễ trên 7 ngày: 1,70 điểm
  \item 79,2\% review của nhóm trễ trên 7 ngày là tiêu cực
\end{itemize}
\note{[S45] Lời nói: một đến hai câu, có số.}
\end{frame}
```

Frame có hình (hình nằm trong `figures/`):
```latex
\begin{frame}{18/74 danh mục (24,3\%) tạo 80\% GMV}
\muc{3.1 · Khám phá dữ liệu}
\begin{center}\anh[0.7\textheight]{3-3-1_pareto_category.png}\end{center}
\note{[S43] ...}
\end{frame}
```

Frame hai cột (chữ bên trái, hình bên phải):
```latex
\begin{frame}{Mô hình kinh doanh hai phía: seller được thu hút, người mua mua qua sàn}
\muc{2.1 · Nghiệp vụ}
\begin{columns}[T]\begin{column}{0.4\textwidth}
\begin{itemize}
  \item Business Model Canvas 9 ô
\end{itemize}
\end{column}\begin{column}{0.58\textwidth}
\begin{center}\anh[0.74\textheight]{3-2-3_business_model_canvas.png}\end{center}
\end{column}\end{columns}
\note{[S14] ...}
\end{frame}
```

Frame có bảng:
```latex
\begin{frame}{Hai hệ thống nguồn có 11 bảng, 121 MB và 1.559.764 dòng}
\muc{2.4 · Dữ liệu nguồn}
\begin{center}\adjustbox{max width=\linewidth,max height=0.5\textheight}{\scriptsize\begin{tabular}{lrr}
\toprule
\textbf{Bảng nguồn} & \textbf{Số dòng} & \textbf{MB} \\
\midrule
oltp.orders & 99.441 & 16,84 \\
\bottomrule
\end{tabular}}\end{center}
\note{[S33] ...}
\end{frame}
```

**Chèn hình từ `figures/`.** Tải PNG lên thư mục `figures/` của project Overleaf, giữ **đúng tên file** (ví dụ `2-5_erd_oltp_gach_chan.png`); trong `.tex` dùng `\anh[chiều cao tối đa]{tên-file.png}` (giữ tỉ lệ, không tràn khung). Hình nháp hiện có đã nằm sẵn trong `figures/` của zip; vẽ lại bằng draw.io thì tải lên **ghi đè** cùng tên.

**Ghi mục barem ở góc.** Dòng `\muc{2.4 · Dữ liệu nguồn}` đặt ngay sau `\begin{frame}`: hiện nhãn nhỏ ở góc trên bên phải. Dùng đúng nhãn của mục trong bảng phân công (ví dụ `2.4 · Dữ liệu nguồn`, `3.3 · ETL`, `4 · DB2 Giao hàng và trải nghiệm khách`).

**Tiêu đề là câu kết luận có số.** Tiêu đề nêu điều slide chứng minh, kèm số lấy từ truy vấn thật: "Giao trễ làm điểm review rơi từ 4,29 xuống 1,70", không phải "Phân tích review". Tiêu đề dài tối đa khoảng hai dòng.

**Biên dịch bằng LuaLaTeX** (không dùng pdfLaTeX): theme dùng `fontspec` và font Lato.

**Lỗi thường gặp và cách sửa.**

| Hiện tượng | Cách sửa |
| --- | --- |
| `File 'xxx.png' not found` | chưa tải hình lên `figures/` hoặc sai tên (phân biệt hoa/thường) |
| `Missing $ inserted` hoặc chữ lạ khi có `_` | trong nội dung viết `\_`; trong **tiêu đề frame** viết `\symbol{95}` (ví dụ `fact\symbol{95}order\symbol{95}fulfillment`), không dùng `\_` |
| `Misplaced alignment tab character &` | viết `\&` |
| Dấu `%` làm mất phần còn lại của dòng | viết `\%` |
| `Undefined control sequence` | gõ sai lệnh hoặc thiếu gói; chỉ dùng lệnh trong mẫu ở trên |
| Mũi tên hiển thị sai | dùng `$\rightarrow$` |
| Gạch nối dài | dùng `--` cho dấu gạch giữa số (`2017--2018`) |
| Tiêu đề bị cắt hoặc tràn | rút ngắn tiêu đề (theme cắt tiêu đề ở hai dòng) |
| Bảng tràn khung | bọc bằng `\adjustbox{max width=\linewidth,max height=0.5\textheight}{...}` như mẫu |
| `Overfull \vbox` | hình hoặc bảng quá cao: giảm tham số trong `\anh[0.6\textheight]` |
| Biên dịch quá lâu hoặc hết thời gian trên Overleaf | dùng `thu-mot-phan.tex` (xem trên) |
| Khung đỏ "CHÈN HÌNH" còn sót | thay `\khungchen{...}` bằng `\anh{...}` khi đã có hình; tìm `khungchen` trong file của mình để chắc không còn sót |

Còn lỗi khác: xem dòng báo lỗi đầu tiên trong *Logs and output files* (dòng bắt đầu bằng `!`), chụp lại và hỏi trong nhóm.

## 5. draw.io

- **Mở file có sẵn.** Mở <https://app.diagrams.net> (hoặc draw.io Desktop) → *File → Open from → Device* → chọn file `.drawio` trong `docs/diagrams/` (cũng có bản trên `03_drawio`). Bản có sẵn là bản nháp sinh tự động, ghi chữ **BẢN NHÁP** trên PNG: sửa lại cho gọn, xoá chữ BẢN NHÁP khỏi bản chính thức.
- **Quy ước màu.**

| Đối tượng | Màu |
| --- | --- |
| fact | cam `#F4A261` |
| dimension | xanh dương `#8ECAE6` |
| bảng tham chiếu, lớp trung gian | xám `#E5E7EB` |
| nguồn / dữ liệu tốt | xanh lá `#CDE8D6` |
| chú ý, điểm thu thập dữ liệu | vàng `#FFF3C4` |
| nhóm phụ | tím `#E2D4F0`, hồng `#F8C8DC`, xanh ngọc `#B7E4DA` |

- **Font:** Segoe UI (hoặc Arial); cỡ chữ trong khối ≥ 12 để đọc được trên slide; mũi tên dùng nét liền, nối đúng khối.
- **Xuất PNG giữ đúng tên file cũ:** *File → Export as → PNG*, chọn *Zoom* sao cho chiều rộng ảnh khoảng 2000 px trở lên (tương đương 200 dpi cho khổ 10 inch; nếu hộp thoại có ô DPI thì chọn 200), bật *Include a copy of my diagram* để mở lại sửa được, nền trắng. Đặt tên theo bảng phân công (ví dụ `3-2_kien_truc_cac_lop.png`).
- **Nộp:** file `.drawio` (ghi đè file cũ trong `03_drawio`) và PNG (cùng thư mục). PNG dùng trong slide thì đặt thêm vào `04_Docs/tex-nop/figures/`. Lỗi thầy hay bắt của từng sơ đồ ghi ở file của người phụ trách.
