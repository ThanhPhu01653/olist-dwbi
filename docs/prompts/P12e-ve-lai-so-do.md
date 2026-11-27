# P12e – Vẽ lại các sơ đồ còn chữ nhỏ

Làm trên nhánh `phase/P12e`. Xong thì merge vào `main` và push. Không sửa `huong-dan/`. Không đổi số liệu, câu chữ hay khung chờ. Đọc `handoff/2026-11-25-P12d-hinh-to.md`, mục "Hình trong bộ chính chưa vẽ lại".

## Bối cảnh
- P12d đã làm hình to và vẽ lại biểu đồ, nhưng còn **19 sơ đồ trong bộ chính** có chữ chỉ 1,2–6 pt sau khi chèn. Tệ nhất là constellation ở trang 101 (1,2 pt).
- Checker `--pdf` chỉ đo chữ của hình có trong `_manifest.json`, nên những hình này lọt qua mà không báo gì.
- Một số sơ đồ là bản nháp mà thành viên có thể vẽ lại bằng draw.io. **Vẫn làm bản nháp mới, to và rõ.** Nếu sau này thành viên nộp bản draw.io thì chỉ thay file.

## 1. Quyết định về 4 biểu đồ đã rút gọn ở P12d
- **Giữ:** chất lượng dữ liệu (10 loại lỗi), phân bố (bỏ hàng boxplot), GMV theo bang.
- **Sửa** `3-3-1_late_rate_by_state`: thay "14 bang cao nhất" bằng **7 bang trễ nhiều nhất và 7 bang trễ ít nhất**, có vạch ngắt giữa hai nhóm, để thấy được tương phản Bắc/Đông Bắc với Sudeste mà `\KetLuan` đang nói. Ghi chú nhỏ "13 bang khác ở dự phòng".

## 2. Checker: đo mọi hình, không chỉ hình trong manifest
Trong `--pdf`, với mọi ảnh trong bộ chính không có trong manifest:
- ước tính cỡ chữ = thu phóng × cỡ chữ gốc. Cỡ chữ gốc lấy từ một bảng khai báo `figures/slide/_nguon_chu.json` (tên file → cỡ chữ nhỏ nhất trong file gốc); không khai báo thì giả định 10 pt;
- **LỖI** nếu dưới 9 pt và hình do script vẽ (loại 1, 2);
- **NÊN** nếu là ảnh chụp hoặc hình thành viên (loại 3, 4), kèm tên người cần vẽ lại theo cột "Ai" trong handoff P12d.

## 3. Vẽ lại (đều qua `scripts/slide_fig.py` hoặc cùng hằng số kích thước, ghi manifest)

Nguyên tắc chung:
- **Bố cục ngang** cho khung khoảng 2,45 : 1.
- **Chữ sau khi chèn ≥ 9 pt**, tên khối ≥ 10 pt.
- **Sơ đồ quá nhiều chi tiết thì không thu nhỏ chữ.** Chọn một trong hai cách:
  - (a) bản tổng quan chỉ giữ tên khối và mũi tên, chi tiết (cột, kiểu dữ liệu) chuyển sang dự phòng;
  - (b) tách thành 2–3 lớp bấm `\only`, mỗi lớp tô một phần.
- **Bảng thì không dùng ảnh**, viết lại bằng `BangTC` (chữ thật, tự to theo slide).

| Hình (trang) | Cách làm |
| --- | --- |
| `3-3-4_constellation.png` (101), `3-3-4_constellation_sl.png` (4) | Bản tổng quan: 6 fact (màu cam) ở giữa, 10 dimension dùng chung (màu xanh) xung quanh, chỉ có tên bảng, không có cột. Nếu không vừa 9 pt thì tách 2 lớp: mart bán hàng/giao hàng và mart seller/funnel. Bản có cột chuyển sang dự phòng. |
| `3-3-4_erd_dw.png` (103), `3-5_data_model_vat_ly.png` (102) | Tách lớp bấm theo từng nhóm fact. Mỗi lớp một fact với các dimension của nó, chỉ cột khoá và 4–6 cột chính, có ký hiệu PK/FK. |
| `3-5_data_mart.png` (105) | Bốn mart thành 4 khối ngang, mỗi khối ghi tên các view chính. Hoặc chuyển thành `BangTC` mart → view → câu hỏi. |
| `3-4-1_pipeline_sl.png` (6) | Một hàng ngang 6–8 khối. Dùng lại cách vẽ của sơ đồ pipeline mới trong `p12d_diagrams.py`. |
| `3-3_etl_jobs.png` (76) | Sơ đồ ngang sáu giai đoạn. Hoặc `BangTC` giai đoạn → việc → số test. |
| `3-4-3_before_after_orders.png` (78), `3-4-3_before_after_geolocation.png` (79) | Bỏ ảnh. Viết lại bằng `\TruocSau` hoặc `BangTC` (3–5 dòng ví dụ, cột trước/sau). Giữ nguyên số liệu từ `export_samples`. |
| `3-5-1_benchmark.png` (109) | Vẽ lại qua `slide_fig.py` nếu do script tạo. Nếu là ảnh thành viên thì chỉ khai báo vào `_nguon_chu.json`. |
| BPMN ×2 (13, 14), canvas (19), cây nghiệp vụ (21), cây yêu cầu (24), ERD OLTP (9) | Bản nháp do `bootstrap_report`/`gen_bmc` vẽ. **Không chạy `bootstrap_report.py`**: tách phần vẽ hình ra script riêng (ví dụ `scripts/p12e_drafts.py`) rồi vẽ lại theo chiều ngang. Canvas 9 ô: lưới 5 cột ngang như mẫu chuẩn, mỗi ô tối đa 3 dòng chữ. ERD: tách 2 lớp (bán hàng, CRM) nếu cần. |
| Data flow ×3 (36, 37, 42), taxonomy (39) | Như trên. Data flow chỉ giữ hệ thống, luồng và tần suất. Taxonomy nếu là cây thì vẽ ngang; nếu là bảng thì viết lại bằng `BangTC`. |

- Mỗi sơ đồ vẽ lại thì lưu vào `figures/slide/`. **Báo cáo vẫn dùng hình cũ.**
- Frame dùng hình đó đổi đường dẫn, giữ `\KetLuan` và `\note`.
- Khung chờ và nhãn `\canxacnhan` (ví dụ "nhóm xác nhận" ở canvas) giữ nguyên.

## 4. Quy tắc vẽ cho thành viên (draw.io)
Thêm vào `QUY-TAC-TRINH-BAY.md` mục 6 một đoạn ngắn để Phú gửi nhóm. Điền lại các con số theo số đo thật của P12d:
- **Hình đầy khung:** khung vẽ khoảng **860 × 350 px**, chữ tối thiểu **20 px**, tên khối 22–24 px.
- **Hình đặt cạnh chữ (`\HinhChu`):** khung khoảng **550 × 350 px**, chữ tối thiểu 20 px.
- Không đặt tiêu đề trong hình, viền trắng 10 px, xuất PNG zoom 300%.
- Không vừa thì tách thành 2 hình, không thu nhỏ chữ.

## 5. Kiểm tra
1. Chạy `latexmk -lualatex main.tex`. Không lỗi, không Overfull.
2. Chạy `kiem_tra_slide.py --strict` và `--pdf`. Bộ chính 0 LỖI. Phần NÊN còn lại chỉ là hình thành viên hoặc ảnh chụp, kèm tên người.
3. Chạy `--anh` cho mọi trang đã sửa. Mở từng ảnh, kiểm chữ đọc được ở 1280 px.
4. Tạo `slides/_xem_truoc/truoc-sau-so-do-*.png` cho constellation, canvas, data flow, before–after.
5. Báo cáo vẫn biên dịch và vẫn dùng hình cũ.
6. Tạo lại `slides_overleaf.zip`, `report_overleaf.zip`, `slides/main.pdf`.

## Kết thúc
- Commit đúng file, merge, push.
- Handoff: `handoff/2026-11-25-P12e-so-do.md`.

Báo lại cho Phú:
- bảng hình: cỡ chữ trước và sau, cách làm, số lớp bấm;
- số trang bộ chính trước và sau;
- danh sách NÊN còn lại theo người;
- đoạn quy tắc draw.io (mục 4) để Phú gửi nhóm;
- ảnh trước/sau.
