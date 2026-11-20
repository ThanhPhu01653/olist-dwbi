# Quy tắc trình bày slide (chiếu bằng máy chiếu)

Áp dụng cho mọi slide trong `slides/sections/`, kể cả slide do Claude Code sinh ra.

Hai công cụ đi kèm:
- **Macro bố cục:** `slides/bocuc.sty` (đã nạp trong `main.tex`).
- **Kiểm tra tự động:** `python scripts/kiem_tra_slide.py --strict` phải trả về 0 LỖI trước khi commit slide.

Mã quy tắc (R1–R9) trùng với mã trong báo cáo của script kiểm tra.

## 1. Vì sao cần quy tắc

Slide 16:9 chiếu trong phòng học bị mờ, ngược sáng, người ngồi cuối cách màn hình 8–10 m. Thứ đọc được trên laptop thường không đọc được trên máy chiếu:
- Bảng `\scriptsize` và chữ trong ảnh chụp màn hình không đọc được.
- Hai ảnh đặt cạnh nhau, mỗi ảnh còn một nửa: không ai nhìn rõ ảnh nào.
- Tiêu đề dài bị theme cắt ở một dòng, mất đúng phần kết luận.

Nguyên tắc chung:
- Mỗi slide **một ý**.
- Người xem hiểu ý đó trong **5 giây**.
- Chi tiết để trong ghi chú người nói (`\note{}`), không để trên slide.

## 2. Quy tắc cứng (script báo LỖI)

| Mã | Quy tắc | Cách sửa |
| --- | --- | --- |
| R1 | Tiêu đề tối đa 80 ký tự, là **câu kết luận có số** | Bỏ vế phụ, giữ con số chính; vế phụ đưa xuống `\KetLuan` |
| R2 | Tối đa **1 hình nhìn thấy cùng lúc** | Hai ảnh: dùng `\only<1>{...}` và `\only<2>{...}` (bấm để chuyển), hoặc tách 2 slide |
| R3 | Không dùng `\scriptsize`, `\footnotesize`, `\tiny` cho nội dung | Thân bài `\normalsize`; bảng `\small` (môi trường `BangTC`); chỉ ghi nguồn (`\Nguon{}`) được chữ nhỏ |
| R4 | Không đặt hình trong cột hẹp hơn 58% | Hình đứng một mình (`\HinhLon`, `\AnhChup`); nếu cần chữ bên cạnh thì dùng `\HinhChu` (hình 60%, chữ tối đa 3 ý) |
| R5 | Tối đa 5 gạch đầu dòng, mỗi ý tối đa 2 dòng | Gộp ý, chia slide, chi tiết vào `\note` |
| R6 | Bảng tối đa 8 dòng (tính cả tiêu đề và dòng tổng), tối đa 5 cột | Gom các dòng nhỏ (ví dụ "3 topic khác"), tách bảng, hoặc chuyển sang biểu đồ |
| R7 | `\KetLuan` nằm trên **một dòng** (tối đa 85 ký tự) | Viết lại ngắn; không dùng `\vfill` trước thanh kết luận |

## 3. Nên làm (script báo NÊN)

| Mã | Quy tắc |
| --- | --- |
| R6 | Bảng dùng môi trường `BangTC`, không dùng `tabular` thường |
| R7 | Slide có hình hoặc bảng thì có `\KetLuan{}`: một câu nói người xem phải nhớ gì, có số |
| R8 | Không thu nhỏ hình dưới 0,45`\textheight`; mặc định `\HinhCao` là vừa |
| R9 | Tối đa khoảng 70 từ nhìn thấy trên một trang (không tính bảng) |

Ngoại lệ có lý do: thêm dòng chú thích `% cho-phep: R5 <lý do>` trong frame. Script sẽ bỏ qua mã đó cho frame này.

## 4. Sáu mẫu slide (chọn đúng một mẫu cho mỗi slide)

| Mẫu | Khi nào | Mã LaTeX |
| --- | --- | --- |
| **A. Hình lớn** | Sơ đồ kiến trúc, biểu đồ | `\HinhLon{file}` + `\KetLuan{...}` |
| **B. Minh chứng** | Ảnh chụp màn hình công cụ (MinIO, Spark UI, dbt, terminal, Power BI) | `\AnhChup{file}` hoặc `AnhKhoanh` (khoanh đỏ đúng chỗ cần nhìn) + `\KetLuan{...}` |
| **C. Số lớn** | Kết quả, tổng kết, mở đầu một phần | `\HangSo[3]{\So{16/16}{bảng khớp}\hfill\So{...}{...}\hfill\So{...}{...}}` + tối đa 2 ý |
| **D. Bảng** | So sánh có cấu trúc, tối đa 8 dòng | `\begin{BangTC}{lXrr}...\end{BangTC}` + `\KetLuan{...}`; dòng quan trọng bắt đầu bằng `\DongNhan` |
| **E. Trước / sau** | Lỗi và cách sửa, trước và sau tối ưu | `\TruocSau{Trước}{...}{Sau}{...}` + tối đa 2 ý + `\KetLuan{...}` |
| **F. Gạch đầu dòng** | Giải thích khái niệm, quy trình ngắn | `itemize` tối đa 5 ý, chữ `\normalsize` |

**Hình + chữ** (`\HinhChu`) chỉ dùng khi hình là biểu đồ vẫn đọc được ở 60% chiều rộng và chữ tối đa 3 ý ngắn. Hình luôn ở bên trái.

## 5. Ảnh chụp màn hình

1. **Cắt sát nội dung.** Chỉ giữ phần chứng minh điều tiêu đề nói; bỏ thanh trình duyệt, khoảng trống, menu.
   - Tỉ lệ rộng/cao nên từ 1,4 đến 2,4.
   - Ảnh dọc (như Spark UI) cắt ra phần cần xem.
   - Dùng `python scripts/cat_anh.py <gốc> <mới> --box trái trên phải dưới` hoặc `--trim`.
   - Không sửa file gốc trong `figures/human_takes/`.
2. **Khoanh chỗ cần nhìn.** Ảnh terminal hoặc bảng dày chữ thì dùng `AnhKhoanh` với `\khoanh{x0}{y0}{x1}{y1}` (toạ độ 0..1 tính từ góc dưới trái) và `\nhan{x}{y}{...}`.
3. **Mỗi ảnh một slide.** Hai ảnh của cùng một minh chứng thì dùng `\only<1>`, `\only<2>`.
4. **Chữ trong ảnh phải đọc được** khi xem trang PDF ở 1280 px chiều rộng. Không đọc được thì cắt nhỏ vùng hơn, hoặc ghi con số chính vào `\KetLuan`.

## 6. Sơ đồ (draw.io, Mermaid, matplotlib)

- **Vẽ cho slide 16:9:** khung ngang, tối đa khoảng 12 khối. Chữ trong sơ đồ sau khi chèn tối thiểu tương đương 12 pt, tức chữ trong file gốc khoảng 1/40 chiều cao ảnh.
- **Sơ đồ chi tiết (như kiến trúc tổng):** tách thành 1 slide tổng quan với ít khối, rồi 1–2 slide phóng to từng phần. Không thu nhỏ cả sơ đồ vào một trang.
- **Biểu đồ matplotlib:** `figsize=(12, 6)`, chữ trục tối thiểu 14, nhãn số trên cột tối thiểu 13, bỏ tiêu đề trong hình (tiêu đề đã có trên slide).
- **Màu theo quy ước:** fact màu cam, dimension màu xanh, nhấn mạnh màu đỏ HUST.

## 7. Tiêu đề và chữ

- **Tiêu đề:** câu kết luận có số. Ví dụ: "Gold khớp kho ở 16/16 bảng", không phải "Kết quả đối soát". Tối đa 80 ký tự.
- **`\KetLuan`:** điều người xem cần nhớ, khác với tiêu đề hoặc nói rõ hơn tiêu đề.
- **Code trong slide:** chỉ tên bảng, tên lệnh ngắn bằng `\texttt`. Không chép khối code dài; cần thì chụp ảnh và khoanh.
- **Nói nhiều hơn chữ:** câu giải thích, nguồn số liệu, đường dẫn file đều đưa vào `\note{}`.

## 8. Quy trình khi làm hoặc sửa slide

1. Chọn mẫu (mục 4) cho từng slide trước khi viết.
2. Biên dịch, rồi chạy:
   ```text
   python scripts/kiem_tra_slide.py --strict slides/sections/<file>.tex
   ```
   Sửa đến khi hết LỖI.
3. Xuất ảnh để xem như trên máy chiếu (cần `pip install pymupdf`):
   ```text
   python scripts/kiem_tra_slide.py --anh slides/main.pdf <trang đầu>-<trang cuối>
   ```
   Mở `slides/_xem_truoc/ghep-*.png` và xem từng trang. Tiêu đề có bị cắt không? Chữ có đọc được không? Có chạm chân trang không?
4. Chỉ commit khi cả bước 2 và bước 3 đều đạt.
