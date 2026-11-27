# P12b – Gọn slide: chỉ giữ cái lớn, gộp slide thưa

Làm trên nhánh `phase/P12b`. Xong thì merge vào `main` và push. Đọc lại `slides/QUY-TAC-TRINH-BAY.md`, `slides/bocuc.sty` và `handoff/2026-11-23-P12-checklist.md` trước khi sửa.

## Bối cảnh

Sau P12, bộ chính có khoảng 182 frame. Slide đang **dài dòng** theo hai kiểu:

1. **Báo cáo mọi lỗi nhỏ và mọi quyết định nhỏ.**
   - Lỗi nhỏ: dòng mồ côi được thử lại, khoảng thời gian âm thành NULL, `trim()` của Trino, khoá thay thế…
   - Quyết định nhỏ: từng fact một trang, từng dimension một trang…

   Người nghe không nhớ được và thầy không chấm những thứ này. Slide chính chỉ nói cái **lớn và quan trọng**. Cái nhỏ chuyển vào `\note{}` hoặc `99-du-phong.tex` (để trả lời khi bị hỏi).
2. **Tách một ý thành nhiều slide một dòng.** Ví dụ: Tình huống, Phát hiện, Quyết định mỗi cái một slide; trang mở cho từng khối nhỏ. Khi chiếu trông như dàn ý chưa viết xong.

   Một slide **được phép có nhiều chữ hơn**: bảng kèm 2–3 gạch đầu dòng, hoặc thẻ số kèm giải thích, trong giới hạn R5 và R6. Gộp slide thưa vào slide cùng ý, đừng làm đầy từng slide một.

## Nguyên tắc
- **Chỉ chuyển, không xoá.** Frame bỏ khỏi bộ chính thì chuyển nguyên sang `99-du-phong.tex`, nhóm theo phần, giữ `\muc`. Riêng số liệu nhỏ chỉ cần chuyển vào `\note` của slide gộp.
- **Không đổi số liệu**, không thêm nhận định mới.
- **Mỗi dòng trong bảng đối chiếu checklist** (handoff P12) vẫn phải có ít nhất một slide trong bộ chính. Tên mục của thầy giữ nguyên trong tiêu đề (R1).
- **Khung chờ (`\khungchen`, `\canxacnhan`):**
  - không xoá, không đổi tên;
  - nếu frame chứa khung chờ được chuyển sang dự phòng, ghi khung đó là "không bắt buộc" trong bảng khung chờ để thành viên bỏ qua;
  - nếu gộp hai frame có khung chờ thì giữ cả hai khung, dùng `\only<1>` / `\only<2>`.
- **Giữ nguyên** frame "Quyết định" của từng dashboard (thành viên sẽ tự sửa câu chữ). Chỉ được gộp frame này với frame Phát hiện như mô tả ở mục 3.

## 0. Commit trước

`scripts/gen_dashboard_docs.py` và `huong-dan/dashboards/*.md` đang có thay đổi chưa commit, Phú đã duyệt. Nội dung: bỏ "(Phú dựng file gốc, tổng hợp và chỉnh sửa)" và "quyết định ngày 13/11" để giọng trung lập.

Commit riêng các file này. Từ nay sinh lại tài liệu dashboard phải giữ giọng đó.

## 1. Quy tắc và checker
- Thêm vào `QUY-TAC-TRINH-BAY.md` mục **"Nói cái lớn"**:
  - bộ chính chỉ giữ kết quả, quyết định thiết kế lớn và vấn đề lớn (tối đa 2–3 vấn đề mỗi chương);
  - chi tiết đưa vào `\note` hoặc dự phòng;
  - một ý một slide, nhưng không tách một ý thành nhiều slide một dòng.
- Thêm vào `kiem_tra_slide.py` mức **NÊN** "slide thưa" cho frame thoả cả hai điều kiện:
  - không có hình, bảng, `\HangSo`, `\TruocSau`, `\khungchen` hay `tikzpicture`;
  - danh sách có tối đa 3 mục, mỗi mục dưới 90 ký tự.

  Bỏ qua trang tiêu đề, trang chuyển phần và trang cảm ơn. Cách sửa gợi ý: gộp vào slide cùng ý.
- Thêm vào `bocuc.sty` macro `\LoTrinh{Mục 1, Mục 2, ...}{k}`:
  - một hàng ô đánh số nối bằng mũi tên, tối đa 6 ô;
  - ô thứ `k` tô màu `hustmain`; `k = 0` thì không tô ô nào.

  Dùng **chỉ** cho trang mở của chương, phần và khối khám phá dữ liệu. Thêm mẫu vào `slides/mau/mau-bo-cuc.tex`.

## 2. Mục tiêu số frame trong bộ chính

Mục tiêu là con số định hướng, lệch ±2 được.

| File | Hiện tại | Mục tiêu | Gợi ý |
| --- | ---: | ---: | --- |
| `01a` | 23 | 16 | Gộp 3 slide đầu về quy trình. "Sáu chủ điểm" và 4 slide "Yêu cầu theo chủ điểm" thành 2 slide (bảng chủ điểm × câu hỏi × KPI). |
| `01b` | 11 | 8 | Gộp 2 slide quy mô, 2 slide tần suất. 3 slide ERD thành 2 (dùng `\only` nếu cần 2 hình). |
| `02a` | 26 | 18 | Một trang mở `\LoTrinh` cho cả phần. Bỏ 5 trang mở khối: nhãn `\muc` đã cho biết đang ở khối nào. Gộp 2 slide phân bố thời gian, 2 slide Pareto, 2 slide STL (dùng `\only`). |
| `02b` | 53 | 32 | Xem mục 3 |
| `03` | 38 | 26 | Xem mục 3 |
| `04` | 22 | 16 (+1 slide AI) | Xem mục 3 |
| `05` | 6 | 5 | Xem mục 3 |

## 3. Gợi ý gộp và chuyển

### `02b` (Người 3)
- **Kiến trúc:** 5 → 3. Slide "tách lớp giúp đối soát" chuyển sang ETL.
- **ETL jobs:** giữ trang tổng quan sáu giai đoạn và haversine. SCD2 bằng window function, khoảng thời gian âm thành NULL, dòng mồ côi thử lại: chuyển sang dự phòng.
- **Before – after:** 4 → 2.
- **Nạp tăng dần:** 4 → 2, giữ "incremental trùng nạp full 16/16".
- **Kiểm thử, nhật ký, dựng lại, giám sát:** 4 → 2.
- **Dimension:** giữ số dòng, nhóm dimension, hệ thống chiều khái niệm, SCD2. `dim_seller`, chiều rác và role-playing, Unknown −1: chuyển sang dự phòng, hoặc gộp thành một bảng "kỹ thuật dimension" nếu vừa R6.
- **Data model:** giữ bus matrix, constellation, vật lý, ba loại fact Kimball. Mỗi fact một trang: chuyển sang dự phòng.
- **Data mart:** 2 → 1.
- **OLAP:** 3 → 2.

### `03` (Người 1–4, Người 4 tổng hợp)
- **Tình huống:** gộp 4 slide Tình huống vào slide "Dashboard: bốn dashboard, bốn loại", thành bảng DB | Ai dùng | Câu hỏi chính.
- **Phát hiện + Quyết định:** mỗi dashboard gộp hai slide này thành **một** slide "DBx – Phát hiện và quyết định".
  - Dạng bảng 3 dòng: phát hiện có số → quyết định đề xuất.
  - Câu chữ Quyết định giữ nguyên.
  - Số còn lại chuyển vào `\note`.
- **DAX chính:** giữ trong bộ chính **một** slide DAX chung (vài measure tiêu biểu kèm định dạng điều kiện). 4 slide DAX từng dashboard chuyển sang dự phòng, khung chờ ghi "không bắt buộc".
- **Nguyên tắc thiết kế:** "bố cục", "chủ đề màu" và "quy chuẩn định dạng số" thành 2 slide.
- **Ảnh chụp dashboard:** giữ các slide khung chờ, vì đó là phần thầy chấm.

### `04` (Phú)
- **Bài học lakehouse:** giữ **một**: Silver thiếu đơn mà log không báo, vì cho thấy giá trị của đối soát. Bài học `trim()` chuyển sang dự phòng và chỉ nhắc một dòng trong slide đối soát.
- **Gộp:**
  - CDC với Kafka;
  - Bronze/Silver với Silver bằng nguồn;
  - dbt với lineage (dùng `\only`);
  - độ trễ với time travel.
- **Phần API:** gộp kiến trúc collector với ghép đô thị nếu vừa.
- **Thêm 1 slide "Hướng mở rộng – AI trong Power BI"** trước tổng kết chương 5:
  - bảng tính năng AI có sẵn trong Power BI Desktop mà nhóm dùng: Key Influencers (DB2), Forecast (DB1). Chỉ ghi tính năng có thật trong `huong-dan/dashboards/*.md`;
  - Copilot cần capacity Fabric trả phí (F2 trở lên), nhóm không dùng, chỉ nêu là hướng mở rộng. Ghi `\Nguon{learn.microsoft.com/power-bi/create-reports/copilot-introduction}`;
  - khai phá dữ liệu: hiện có RFM theo quy tắc ở DB2, hướng mở rộng là phân cụm k-means và luật kết hợp danh mục. Chỉ nêu hướng.

### `05` (Người 4)
- **Kết quả:**
  - thẻ số cùng phạm vi với GMV 13,49 triệu (Orders 98.199), hoặc ghi rõ "đơn trong nguồn" nếu giữ 99.441;
  - bỏ gạch đầu dòng lặp lại số đã có trên thẻ.
- **Bài học kỹ thuật:** chỉ giữ 3 vấn đề lớn nhất (một KPI có hai con số; review đúng hạn 4,21 → 4,29; Silver thiếu đơn), phần còn lại vào `\note`.
- **Hạn chế và hướng phát triển:**
  - `BangTC` hai cột Hạn chế → Hướng phát triển, 4–5 dòng, câu dễ hiểu (không dùng "mồ côi", "thử lại");
  - gồm: dữ liệu 2016 thưa, 09/2018 bị cắt; không có chi phí marketing; ngày hứa giao quá rộng; kho chạy theo lô bằng tay; lakehouse trong 4 GB RAM;
  - hướng phát triển gồm cả AI trong Power BI.

### Thống kê đặc trưng (`02a`)
Bảng hiện lấy trên mẫu 5.000 đơn (Excel ToolPak). Tính thêm bằng SQL trên toàn bộ kho mean và median của `price_total` và `lead_days`, rồi:
- ghi vào `\note`;
- sửa `\KetLuan` để nói mẫu và toàn bộ cho cùng kết luận.

Nếu kết luận khác nhau thì báo Phú, không tự sửa.

## 4. Cập nhật hướng dẫn thành viên
- `huong-dan/phan-viec/Nguoi-1..4.md` và `Phu.md` có bảng slide theo người (số trang, tiêu đề, khung chờ): cập nhật theo vị trí mới. Frame chuyển sang dự phòng ghi "dự phòng, không bắt buộc".
- Mục "Chọn slide để nói" của từng người: chọn lại từ bộ chính mới.
- Giữ giọng trung lập: không có hạn ngày, không có "hỏi/báo Phú".
- Thêm vào mục quy tắc trình bày trong `huong-dan/phan-viec/README.md` một câu: "Slide chính chỉ nói cái lớn; lỗi và quyết định nhỏ để ở ghi chú hoặc slide dự phòng".

## 5. Kiểm tra (bắt buộc)
1. Chạy `latexmk -lualatex main.tex`. Không lỗi, không có `Overfull \vbox` ở frame đã sửa.
2. Chạy `python scripts/kiem_tra_slide.py --strict` trên toàn bộ `slides/sections/`: 0 LỖI. Liệt kê các mục "slide thưa" còn lại kèm lý do.
3. Chạy `--anh` cho **mọi** trang đã sửa hoặc gộp. Mở từng ảnh để kiểm: không tràn; bảng đọc được; `\LoTrinh` rõ ở 1280 px.
4. Đối chiếu lại bảng checklist trong handoff P12: mỗi dòng có trang trong bộ chính (cập nhật số trang mới).
5. Đếm khung chờ theo người, tách bắt buộc và không bắt buộc. Tổng số khung không được giảm; chỉ tăng nếu có ảnh mới (ví dụ Key Influencers).
6. Tạo lại `slides_overleaf.zip`, `report_overleaf.zip` (nếu báo cáo dùng chung file) và `slides/main.pdf`.

## Kết thúc
- Commit đúng file đã sửa, merge, push.
- Handoff: `handoff/2026-11-25-P12b-gon-slide.md`.

Báo lại cho Phú:
- số frame bộ chính và dự phòng, trước và sau, theo file;
- danh sách frame đã gộp hoặc chuyển sang dự phòng;
- bảng khung chờ theo người (bắt buộc / không bắt buộc);
- ảnh `slides/_xem_truoc/ghep-*.png` của các trang đã sửa.
