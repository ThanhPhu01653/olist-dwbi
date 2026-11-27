# P12d – Hình to hơn, chữ trong hình to hơn

Làm trên nhánh `phase/P12d`. Xong thì merge vào `main` và push. Không sửa `huong-dan/`. Không đổi số liệu, câu chữ, tiêu đề, `\KetLuan` hay khung chờ. Việc lần này **chỉ là kích thước**.

## Bối cảnh: đo trên `slides/main.pdf` hiện tại

Trang slide cao 255 pt. Đo được:
- thanh tiêu đề và đường đỏ kết thúc ở y ≈ 34,5 pt;
- nhãn `\muc` (overlay) nằm ở y ≈ 37–44 pt, góc phải;
- đường chân trang ở y ≈ 238 pt.

Vùng dùng được cao khoảng **200 pt**. Thế nhưng:
1. **Hình bắt đầu ở y ≈ 57 pt**, bỏ trống hơn 20 pt dưới thanh tiêu đề. Hình có `\KetLuan` chỉ cao **136 pt** (`\HinhCao = 0.60\textheight`); thanh kết luận ở y ≈ 200–220 pt, còn 18 pt trống trên chân trang.
2. **Phần lớn hình bị giới hạn theo chiều cao nên hẹp.** Nhiều hình chỉ rộng 150–260 pt trên khung 428 pt (ví dụ trang 26, 38, 46, 57–59, 61, 102), vì hình gốc gần vuông hoặc dọc trong khi khung trống là khung ngang khoảng 2,5 : 1.
3. **Chữ trong hình rất nhỏ khi chiếu.** Hình do script vẽ ở kích thước lớn (ví dụ 2850 px ở 300 dpi, tức khoảng 9,5 inch), rồi bị thu nhỏ còn khoảng 25% khi chèn. Chữ 12 pt trong hình chỉ còn khoảng 3 pt trên slide, trong khi chữ thân slide là 10–11 pt. Quy tắc mục 6 trong `QUY-TAC-TRINH-BAY.md` (chữ ≥ 12 pt sau khi chèn) chưa được kiểm bằng số nên bị bỏ qua.

## Mục tiêu
- Hình **cao hơn**: dùng hết vùng giữa thanh tiêu đề và chân trang. Sát một chút cũng được (khe tối thiểu khoảng 2–3 pt), nhưng **không đè** lên thanh tiêu đề, nhãn `\muc`, chân trang, và không tràn trang.
- **Chữ trong mọi hình do script vẽ**, sau khi chèn vào slide, tối thiểu **9 pt** (nhãn trục, chú thích, số trên cột). Chữ chính trong hình 10–11 pt, tức ngang chữ thân slide.
- Hình **ngang** cho khớp khung 16:9; không còn hình hẹp giữa khoảng trống lớn.

## 1. Bố cục (`slides/bocuc.sty`, `slides/main.tex` hoặc `hust-override.sty`)

**a. Đo bằng PDF, không đoán.** Viết `scripts/do_vung_slide.py`:
- dùng PyMuPDF đọc `main.pdf`;
- in ra toạ độ đáy thanh tiêu đề, hộp nhãn `\muc`, đỉnh chân trang, và hộp của mọi hình và mọi thanh `\KetLuan` trên từng trang.

Dùng số đo này để đặt các độ dài bên dưới. Ghi số đo trước và sau vào handoff.

**b. Kéo nội dung lên sát thanh tiêu đề.** Giảm khoảng cách mặc định từ tiêu đề đến nội dung (hiện khoảng 22 pt) xuống khoảng 6–8 pt. Xử lý nhãn `\muc`, chọn một trong hai cách:
- **(ưu tiên)** đưa nhãn vào trong thanh tiêu đề, bên phải, trước logo. Chữ trắng trên nền xanh của thanh, không đè chữ tiêu đề. Tiêu đề dài nhất là 65 ký tự, hãy kiểm với tiêu đề dài nhất;
- hoặc giữ chỗ cũ, nhưng nội dung bắt đầu ngay dưới đáy nhãn.

**c. Đặt lại độ dài trong `bocuc.sty`** theo số đo:
- `\HinhCao` (hình có `\KetLuan` bên dưới) = từ đỉnh vùng nội dung đến đỉnh `\KetLuan`, trừ khe 3 pt. Dự kiến khoảng **165–175 pt**, so với 136 hiện tại;
- `\VungCao` (hình không có `\KetLuan`) = đến chân trang trừ khe 3 pt. Dự kiến khoảng **190 pt**;
- `\KetLuan` gọn lại: khoảng cách trên 6 pt → 3 pt, `inner sep` 5 pt → 3 pt, chữ giữ nguyên;
- `\HinhChu`, `AnhKhoanh`, `\AnhChup` dùng cùng chiều cao mới;
- frame có thêm 1–2 gạch đầu dòng ngoài hình thì dùng độ dài phụ (ví dụ `\HinhCaoCoY`) cũng đo từ PDF. Không để mỗi frame tự đặt `height=0.xx\textheight`.

**d.** Tìm các frame đang tự đặt chiều cao nhỏ (`height=`, `[0.4\textheight]`, …) trong mọi file slide. Đổi sang macro mặc định, trừ khi frame cần chừa chỗ cho chữ. Chỉ đổi tham số kích thước, không đổi gì khác.

## 2. Chữ trong hình: vẽ lại hình do script tạo

**a. Kiểm kê.** Liệt kê mọi hình dùng trong **bộ chính** (không tính `99-du-phong.tex`) và phân loại:
- (1) biểu đồ do script vẽ (matplotlib/seaborn);
- (2) sơ đồ do script vẽ (graphviz, mermaid, matplotlib: cây, mindmap, kiến trúc, lineage, pipeline…);
- (3) ảnh chụp màn hình;
- (4) hình thành viên tự vẽ hoặc tự chụp (draw.io, Excel, Power BI).

Với mỗi hình ghi script tạo ra nó, kích thước khi chèn (pt), và cỡ chữ nhỏ nhất ước tính sau khi chèn.

**b. Thêm `scripts/slide_fig.py`** (dùng chung cho mọi biểu đồ của slide):
- các hằng số kích thước khung đo ở mục 1, tính bằng inch: hình đầy khung có `\KetLuan`, hình đầy khung không có `\KetLuan`, hình 60% của `\HinhChu`;
- hàm tạo `figure` **đúng bằng kích thước khi chèn**, để tỉ lệ thu phóng khoảng 1;
- `rcParams`: chữ chính 10–11 pt, nhãn trục, tick, chú thích tối thiểu 9 pt, nét dày hơn, `dpi=300`;
- không có tiêu đề trong hình (tiêu đề nằm ở frame);
- cắt viền trắng (`bbox_inches="tight"`, pad nhỏ).

**c. Vẽ lại mọi hình loại (1) và (2) trong bộ chính** bằng script gốc, qua `slide_fig.py`.
- Lưu bản slide riêng, ví dụ `figures/slide/<tên>.png` hoặc `<tên>_slide.png`.
- **Báo cáo vẫn dùng hình cũ**: không ghi đè file báo cáo đang dùng.
- Đổi đường dẫn trong frame sang bản slide.
- Số liệu, màu, loại biểu đồ giữ nguyên. Chỉ đổi khổ hình, cỡ chữ, bố cục (ví dụ chú giải đặt ngang trên đầu, nhãn trục ngắn lại).
- **Sơ đồ dạng cây hoặc mindmap** (ví dụ cây phân tích DB1–DB4 ở trang 26–29, cây nghiệp vụ, sơ đồ kiến trúc): vẽ lại theo chiều ngang (`rankdir=LR` hoặc tương đương) cho khớp khung 2,5 : 1, giảm khoảng trắng, chữ trong ô ≥ 9 pt sau khi chèn. Cây quá to thì tách thành 2 lớp bấm `\only` (ví dụ nhánh Câu hỏi / nhánh Chỉ số), không thu nhỏ chữ.
- Hình chỉ có trong `99-du-phong.tex` thì không bắt buộc. Nếu cùng script và rẻ thì làm luôn.

**d. Ảnh chụp màn hình (loại 3):** không chụp lại. Cắt sát hơn bằng `scripts/cat_anh.py`, bỏ viền, thanh công cụ và vùng trống không cần, để ảnh hiển thị to hơn trong khung mới. Ghi ra file `_tc.png`, không sửa ảnh gốc.

**e. Hình loại 4:** không sửa. Liệt kê vào handoff kèm cỡ chữ ước tính sau khi chèn, để Phú báo người vẽ nếu quá nhỏ.

## 3. Checker (`scripts/kiem_tra_slide.py`)

Thêm chế độ kiểm trên PDF (ví dụ `--pdf slides/main.pdf`) dùng số đo của mục 1:
- **LỖI** khi hộp hình hoặc hộp `\KetLuan` chạm vùng thanh tiêu đề, nhãn `\muc` hoặc chân trang (khe < 2 pt), hoặc ra ngoài trang;
- **LỖI** khi hình loại (1) hoặc (2) có chữ nhỏ nhất sau khi chèn dưới 9 pt. Cách tính: `slide_fig.py` ghi `figures/slide/_manifest.json` gồm tên file, cỡ chữ nhỏ nhất (pt), chiều rộng figure (inch), dpi. Checker so chiều rộng hiển thị trong PDF với chiều rộng figure để ra tỉ lệ thu phóng, rồi nhân với cỡ chữ. Nối ảnh trong PDF với file theo kích thước pixel; nếu trùng thì so mã băm;
- **NÊN** khi hình chiếm dưới 55% chiều rộng khung mà vẫn chạm trần chiều cao (hình hẹp). Gợi ý: vẽ lại theo chiều ngang.

Cập nhật mục 6 của `QUY-TAC-TRINH-BAY.md` theo cách đo mới. Thêm câu: "biểu đồ cho slide luôn vẽ qua `scripts/slide_fig.py`".

## 4. Kiểm tra (bắt buộc)
1. Chạy `latexmk -lualatex main.tex`. Không lỗi, không `Overfull \vbox`.
2. Chạy `python scripts/kiem_tra_slide.py --strict` trên mọi file `sections/`, và `--pdf slides/main.pdf`. Bộ chính 0 LỖI.
3. Chạy `--anh` cho **toàn bộ trang của bộ chính**. Mở từng ảnh xem trước để kiểm:
   - hình không đè tiêu đề, nhãn, chân trang;
   - chữ trong hình đọc được ở 1280 px;
   - không còn hình hẹp giữa khoảng trống lớn.

   Sửa xong thì xuất và xem lại.
4. Tạo `slides/_xem_truoc/truoc-sau-*.png`: 4 trang tiêu biểu (một biểu đồ, một cây, một ảnh chụp, một `\HinhChu`), trước bên trái, sau bên phải.
5. Báo cáo (`report/`) biên dịch lại không lỗi và vẫn dùng hình cũ.
6. Tạo lại `slides_overleaf.zip` (có `figures/slide/`), `report_overleaf.zip`, `slides/main.pdf`.

## Kết thúc
- Commit đúng file đã sửa, merge, push.
- Handoff: `handoff/2026-11-25-P12d-hinh-to.md`.

Báo lại cho Phú:
- số đo trước và sau: đỉnh vùng nội dung, `\HinhCao`, `\VungCao`, khe tới chân trang;
- số hình đã vẽ lại, đã cắt lại, và danh sách hình loại 4 có chữ quá nhỏ (ai vẽ);
- cỡ chữ nhỏ nhất sau khi chèn: trước và sau, cho bộ chính;
- số trang bộ chính trước và sau;
- ảnh `truoc-sau-*.png` và `ghep-*.png` của bộ chính.
