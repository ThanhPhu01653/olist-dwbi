# Phú – Mở đầu, mở rộng, kết luận, file gốc và ghép file tổng

Chung cho cả nhóm (Drive, Power BI, Overleaf, draw.io): [`README.md`](README.md). File này viết dạng checklist cho Phú; các mục 1–3 và 5–6 giống khung của `Nguoi-1.md` … `Nguoi-4.md`.

## 1. Phần của bạn

| Hạng mục | Nội dung |
| --- | --- |
| Mục barem (báo cáo / slide) | **Mở đầu** · **Ch.5 Mở rộng** (5.1 Lakehouse, 5.2 thu thập API, D8, DB1 trên Superset) · **Ch.6 Kết luận** |
| File slide | `slides/sections/00-mo-dau.tex` (3 frame của Phú; 2 frame lý thuyết rút gọn là của Người 1), `04-mo-rong.tex`, `05-tong-ket.tex`, `99-du-phong.tex` |
| Sơ đồ draw.io | **Kiến trúc Lakehouse** (`5-1_kien_truc_lakehouse.png`); sơ đồ API `5-2_kien_truc_api.png` |
| Dashboard | file gốc `olist_base.pbix`, **D8 Thị trường Brazil**, ghép file tổng, publish, QR |
| Thuyết trình | mở đầu (khoảng 3 phút, 3 slide) và mở rộng + kết luận (khoảng 5–6 phút); thứ tự: Phú → Người 1 → Người 2 → Người 3 → Người 4 → Phú |
| Báo cáo (giai đoạn 2) | `00-*` (bìa, lời mở đầu, đánh giá, viết tắt), `5-1-lakehouse.tex`, `5-2-thu-thap-api.tex`, `06-ket-luan.tex`, phụ lục |

## 2. Barem chấm gì ở phần này

**Hướng mở rộng (tập trung 1–2 hướng)** — các dòng thầy kiểm tra (trích từ bảng nhận xét mẫu; dòng đỏ là chỗ nhóm khác bị trừ điểm):
- Tổ chức hoạt động tiền xử lý dữ liệu trong CSDL/công cụ lập trình.
- **Data lake.**
- Ứng dụng AI/Copilot.
- Sử dụng các ETL tools/Data pipeline.
- **Thu thập dữ liệu thực tế sử dụng API.**
- Tính năng mới của các công cụ (Power BI, …).
- Khai phá dữ liệu (phân lớp, phân cụm, luật kết hợp).
- Sử dụng công cụ trực quan mới (ví dụ Tableau).
- Ngoài ra thầy chê một nhóm dùng **SQLite làm lakehouse: "chưa hợp lý về công nghệ"** và "trình bày lakehouse triển khai chưa rõ".

Ngoài 11 mục: *mức độ thu hút* (số người đặt câu hỏi) và *điểm bổ sung* (hướng mở rộng).

Đối chiếu với nhóm 6 (`docs/doi-chieu-nhom6.md`, thang 5):

| Mục | Nhóm 6 | Nhóm 6 làm gì | Mình làm hơn / cần làm |
| --- | ---: | --- | --- |
| Mở rộng (slide 151–233) | điểm bổ sung 2 | Lakehouse: kiến trúc → các bước triển khai, mỗi bước kèm một slide minh chứng → kết quả; trợ lý hỏi đáp Text-to-SQL | đã có khung chương 5. **Cần làm:** P9 (thu thập API, D8) và P10 (Lakehouse, DB1 trên Superset); xen kẽ slide triển khai và slide minh chứng |
| Bài học (slide 148–150, 235–237) | 4 | bài học về chỉ số và quy trình; tổng kết quy trình, kiến thức, công cụ | phần này do Người 4 gom; Phú dùng ở chương kết luận |

Không được chép câu chữ, số liệu hay hình của nhóm 6.

## 3. Kiến thức cần nắm

**Data lake và lakehouse.** *Data warehouse* lưu dữ liệu đã làm sạch theo lược đồ cố định; *data lake* lưu dữ liệu thô mọi định dạng trên object storage; *lakehouse* thêm lớp **table format có ACID** (Apache Iceberg: giao dịch, time travel) lên object storage để có cả hai. Kho chương 3 (PostgreSQL) có giới hạn mà lakehouse giải quyết: nạp theo lô so với CDC (bắt thay đổi liên tục); `fact_order_fulfillment` ghi đè trạng thái nên mất lịch sử sự kiện; không giữ dữ liệu thô; lưu trữ và tính toán gắn trên một máy; Power BI Import phải refresh. Thầy đã chê SQLite làm lakehouse, nên lưu trữ phải là object storage + table format có ACID. Thiết kế: `docs/prompts/P10-lakehouse.md` (bước 1), kết quả sẽ ở `docs/LAKEHOUSE.md`.

**Medallion Bronze – Silver – Gold.** Bronze: dữ liệu thô nguyên văn; Silver: làm sạch và ghép; Gold: star schema giống kho chương 3, đối soát được từng con số với kho cũ.

**Thu thập dữ liệu qua API (P9).** Olist chỉ có dữ liệu nội bộ, tĩnh. Làm giàu bằng dữ liệu công khai của Brazil: IBGE (bang, đô thị, dân số), Banco Central do Brasil SGS (tỷ giá USD/BRL, lạm phát IPCA), BrasilAPI (ngày lễ). Trả lời câu hỏi Olist không tự trả lời được: doanh thu trên đầu người theo bang, tăng trưởng thực sau lạm phát, GMV quy đổi USD, ngày lễ chính thức. Cách trình bày theo ý thầy: **kiến trúc → triển khai → kết quả**, mọi số liệu từ lần chạy thật. Chi tiết: `docs/prompts/P9-thu-thap-api.md`.

**Superset.** Apache Superset là công cụ BI nguồn mở; dựng lại **DB1 trên Superset** đọc từ tầng Gold của lakehouse (qua Trino), để so sánh với DB1 trên Power BI (cùng số liệu): đáp ứng "sử dụng công cụ trực quan mới".

**Bài học và kết luận.** Kết quả: một kho dữ liệu chạy được từ đầu đến cuối (10 chiều, 6 fact, 17 view mart; 99.441 đơn; GMV 13,49 triệu BRL; 136 kiểm thử đạt 100%; dựng lại 443 giây) và bốn dashboard. Hạn chế nói thẳng: mô phỏng cập nhật chỉ thêm bản ghi mới, chưa có đơn đổi trạng thái giữa chừng; chưa dùng PostGIS (khoảng cách là haversine đường chim bay); điều phối bằng lệnh Python, chưa có lịch tự chạy (`handoff/00-TONG-QUAN.md` mục 9).

## 4. Số liệu và hình có sẵn

| Số liệu | Giá trị | Nguồn |
| --- | --- | --- |
| Tổng quan dự án | 1,56 triệu dòng nguồn → 6 fact, 17 view mart, 4 dashboard | `handoff/00-TONG-QUAN.md` |
| Kết quả kiểm thử | 136 phép đạt 100%, 6/6 đối chiếu EDA | `handoff/2026-11-14-P8-etl.md` |
| Dựng lại toàn bộ | 443 giây, kết quả giống hệt | `handoff/rebuild-report.md` |
| Mô hình Power BI | 38 bảng, 32 quan hệ, 65 measure | `powerbi/olist_base/README.md`; `handoff/2026-11-14-P8c.md` |
| Hạn chế | danh sách | `handoff/00-TONG-QUAN.md` mục 9 |
| Mở rộng (P9, P10) | chưa chạy; điền sau khi làm | `docs/prompts/P9-thu-thap-api.md`; `P10-lakehouse.md` |

## 5. Danh sách slide đề xuất

**Các slide đang có trong `00-mo-dau.tex`** (bảng do script đọc từ file `.tex`; hai frame lý thuyết cuối là của Người 1):

<!-- SLIDES:00-mo-dau.tex -->
| STT | S | Tiêu đề (câu kết luận) | Nội dung chính | Hình / bảng | Trạng thái |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 1 | Xây kho dữ liệu và BI cho 99.441 đơn hàng thương mại điện tử Olist | Học phần MI4214 – Kho dữ liệu và Kinh doanh thông minh; nhóm ...; giảng viên ... | `3-3-4_constellation.png` | đã có |
| 2 | 2 | Bài trình bày gồm năm phần theo thứ tự khảo sát, phân tích thiết kế, dashboard, mở rộng và tổng kết | 2 Khảo sát (nghiệp vụ, yêu cầu, KPI, dữ liệu nguồn, ERD) 3 Phân tích và thiết kế (khám phá dữ liệu, kiến trúc, ETL, chiều khái niệm, data model) 4 Das | – | đã có |
| 3 | 3 | Dự án trong một trang: 1,56 triệu dòng nguồn thành 6 fact, 17 view mart và 4 dashboard | 2 hệ thống nguồn → staging → ODS → kho (10 chiều + 6 fact) → 4 data mart → Power BI | `3-4-1_pipeline.png` | đã có |
| 4 | 4 | Kho dữ liệu là nơi tích hợp dữ liệu hướng chủ đề, biến thiên theo thời gian và không bị ghi đè | Bốn đặc tính của Inmon: hướng chủ đề, tích hợp, biến thiên theo thời gian, không biến động | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: sơ đồ 4 ô (vẽ) |
| 5 | 5 | OLTP tối ưu ghi từng giao dịch, OLAP tối ưu đọc và tổng hợp | OLTP: 9 bảng chuẩn hóa; OLAP: một fact nối các chiều | `3-2-4_erd_oltp.png` | đã có |

*5 frame trong `00-mo-dau.tex` (đếm từ mã `.tex`; cột S là số `[Sxx]` trong ghi chú người nói và trong `slides/slide-script.md`).*
<!-- /SLIDES -->

**Các slide đang có trong `04-mo-rong.tex` và `05-tong-ket.tex`** (khung chờ P9, P10):

<!-- SLIDES:04-mo-rong.tex,05-tong-ket.tex -->
| STT | S | Tiêu đề (câu kết luận) | Nội dung chính | Hình / bảng | Trạng thái |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 115 | [P10] Kiến trúc lakehouse: lớp lưu trữ, định dạng bảng và engine truy vấn nằm cạnh kho PostgreSQL |  | khung chờ | cần ảnh: P10 điền: sơ đồ kiến trúc lakehouse |
| 2 | 116 | [P10] Triển khai lakehouse: nạp, phân lớp và truy vấn mẫu |  | khung chờ | cần ảnh: P10 điền: các bước triển khai |
| 3 | 117 | [P10] Kết quả lakehouse: số liệu đo được so với kho PostgreSQL |  | khung chờ | cần ảnh: P10 điền: bảng kết quả và hình |
| 4 | 118 | [P9] Bài toán: dữ liệu Olist là ảnh chụp tĩnh nên cần nguồn thực tế bổ sung qua API |  | khung chờ | cần ảnh: P9 điền: bài toán |
| 5 | 119 | [P9] Kiến trúc thu thập: từ API đến staging, tần suất gọi và xử lý lỗi |  | khung chờ | cần ảnh: P9 điền: sơ đồ kiến trúc |
| 6 | 120 | [P9] Triển khai thu thập: mã Python, bảng đích và lịch chạy |  | khung chờ | cần ảnh: P9 điền: mã và lược đồ |
| 7 | 121 | [P9] Kết quả thu thập: số dòng thu được và ví dụ phân tích |  | khung chờ | cần ảnh: P9 điền: số liệu và hình |
| 8 | 148 | [P10] DB1 trên Superset: cùng số liệu với Power BI, đọc từ tầng Gold của lakehouse |  | khung chờ | cần ảnh: P10 điền: ảnh chụp DB1 trên Superset |
| 9 | 149 | [P9] Dashboard D8 Thị trường Brazil dựng từ dữ liệu API thu thập thực tế |  | khung chờ | cần ảnh: P9 điền: ảnh chụp D8 |
| 10 | 111 | Kết quả: một kho dữ liệu chạy được từ đầu đến cuối với 136 kiểm thử đạt và bốn dashboard | 10 chiều, 6 fact, 17 view mart; 99.441 đơn; GMV 13,49 triệu BRL | `3-3-4_constellation.png` | đã có |
| 11 | 113 | Hạn chế và hướng phát triển: trạng thái trung gian của đơn, PostGIS, lịch chạy tự động | Mô phỏng cập nhật chỉ thêm bản ghi mới; cơ chế thử lại mồ côi mới được chứng minh bằng test | – | đã có |

*11 frame trong `04-mo-rong.tex`, `05-tong-ket.tex` (đếm từ mã `.tex`; cột S là số `[Sxx]` trong ghi chú người nói và trong `slides/slide-script.md`).*
<!-- /SLIDES -->

**Slide cần thêm** (theo `docs/doi-chieu-nhom6.md`: xen kẽ slide triển khai và slide minh chứng):

| STT mới | Tiêu đề đề xuất | Nội dung chính | Hình / bảng | Nguồn số liệu | Trạng thái |
| ---: | --- | --- | --- | --- | --- |
| P1 | Lakehouse: kiến trúc (thay khung S đầu mục 5.1) | tầng, công cụ, vai trò, vì sao chọn | `5-1_kien_truc_lakehouse.png` | `docs/LAKEHOUSE.md` (sau P10) | chờ P10 |
| P2–P5 | Triển khai lakehouse từng bước, mỗi bước một slide minh chứng (ảnh chụp, lệnh, kết quả) | nạp CDC, Bronze/Silver/Gold, truy vấn mẫu | ảnh chụp | handoff P10 | chờ P10 |
| P6 | Kết quả lakehouse: số liệu đo được, đối soát với kho PostgreSQL | số bảng, số dòng, thời gian truy vấn | bảng | handoff P10 | chờ P10 |
| P7 | DB1 trên Superset cùng số liệu với Power BI | so sánh hai công cụ | ảnh chụp | handoff P10 | chờ P10 |
| P8 | Thu thập API: bài toán, kiến trúc, triển khai, kết quả (4 slide) | IBGE, BCB, BrasilAPI | `5-2_kien_truc_api.png` | `docs/THU_THAP_API.md` (sau P9) | chờ P9 |
| P9 | D8 Thị trường Brazil dựng từ dữ liệu API | dashboard D8 | ảnh chụp D8 | `huong-dan/dashboards/D8.md` (sau P9) | chờ P9 |
| P10 | Kết luận: số kết quả, 3 bài học chính, hạn chế (sửa S đầu `05-tong-ket.tex`) | từ bài học Người 4 gom | bảng | Người 4 (26/11) | cần làm |

Khối lượng: mở đầu 5 frame (3 của bạn + 2 của Người 1), mở rộng 9 frame khung (cộng khoảng 6–8 slide minh chứng khi có P9, P10), kết luận 2 frame, dự phòng 17 frame. **Chọn slide để nói:** mở đầu S1–S3 (khoảng 3 phút); cuối bài: kiến trúc lakehouse (P1), một slide minh chứng triển khai, kết quả (P6), DB1 Superset (P7), thu thập API và D8 (P8, P9), kết luận (P10): khoảng 7 slide trong 5–6 phút.

Trước khi nộp slide: số liệu trong slide mở đầu khớp `handoff/00-TONG-QUAN.md`; mọi slide có `\muc{...}`.

## 6. Sơ đồ draw.io

- `5-1_kien_truc_lakehouse.png`: tầng lưu trữ (object storage), định dạng bảng (Iceberg), engine truy vấn, nguồn (CDC, JSON từ API), Bronze/Silver/Gold, quan hệ với kho PostgreSQL hiện có, BI (Power BI, Superset). **Vẽ theo lớp, không vẽ thành luồng**, có logo công nghệ (như lỗi thầy hay bắt ở `Nguoi-3.md`). Sẽ có file `.drawio` và bản nháp sau P10.
- `5-2_kien_truc_api.png`: collector → landing zone JSON thô → staging → ODS → kho → mart → Power BI. Sẽ có bản nháp sau P9.

## 7. Checklist việc của Phú

### 7.1 Power BI: file gốc, D8, ghép file tổng, publish, QR
- [ ] **File gốc:** mở `powerbi/olist_base/olist_base.pbip` bằng Power BI Desktop, Refresh, đối chiếu số với bảng ở `powerbi/olist_base/README.md` mục 4, rồi lưu `olist_base.pbix`. *Thư mục `powerbi/olist_base/` hiện có thay đổi chưa commit do Power BI Desktop lưu lại (gồm tham số `DataFolder` trỏ vào đường dẫn máy của bạn): trước khi commit, đặt lại `DataFolder` về giá trị mặc định hoặc không commit `expressions.tmdl`.*
- [ ] **Đóng gói:** `olist_base.pbix` lên `02_Dashboard`; 37 file CSV và `olist_geolocation_dataset.csv` lên `01_pBI_data`. Quy tắc: mọi người lưu thành `DBx_<tên>.pbix` trước khi dựng, **không sửa file gốc**.
- [ ] **Measure mới:** nếu ai cần measure chưa có, thêm vào `powerbi/measures.md` và `olist_base`, rồi chạy `python scripts/gen_pbip.py` (ghi đè `powerbi/olist_base/` nên chỉ chạy khi chưa ai dựng trên bản mới) hoặc thêm tay trong file gốc. Không để mỗi người tạo measure riêng trong file riêng, vì khi ghép sẽ mất.
- [ ] **D8 Thị trường Brazil:** sau P9, dựng bằng Power BI từ dữ liệu API; hướng dẫn `huong-dan/dashboards/D8.md` (do P9 viết). Không sửa DB1–DB4 của nhóm.
- [ ] **Ghép file tổng** (4 file `DBx_<tên>.pbix` → `Olist_DW_BI.pbix`), cách làm gợi ý (chưa thử):
  1. Dựng file tổng từ `olist_base.pbix` (cùng mô hình) rồi thêm các trang.
  2. Mỗi trang của một dashboard: mở file của người đó, chọn trang → chọn tất cả visual (Ctrl+A) → Ctrl+C → dán vào trang mới ở file tổng. Dán xong kiểm tra lại định dạng có điều kiện, bộ lọc trang `InWindow` và các tooltip.
  3. **Trang drill-through và tooltip:** cài đặt trang (Page type = Drillthrough, Tooltip, trường drill-through) **không đi theo** thao tác dán visual: đặt lại ở file tổng, hoặc dùng định dạng PBIR (mỗi trang là một thư mục trong `.Report/definition/pages/` của một dự án `.pbip`: sao chép thư mục trang và thêm tên trang vào `pages.json`) nếu mọi người lưu thêm bản `.pbip`.
  4. Sau khi ghép: đối chiếu từng thẻ với `powerbi/measures.md` mục 7; mở từng drill-through và tooltip.
- [ ] **Publish:** *Home → Publish* → *My workspace*; *File → Embed report → Publish to web (public)* → *Create embed code* → sao chép link (`powerbi/model.md` mục 9). Dữ liệu Olist là dữ liệu công khai nên chấp nhận; **không đưa dữ liệu thật của người khác lên**. Nếu tài khoản trường tắt *Publish to web*: dùng tài khoản cá nhân, hoặc xuất PDF/PowerPoint và chụp ảnh.
- [ ] **QR:** mở link công khai trong Microsoft Edge → menu ⋯ → *Share* → *Create QR code for this page* (hoặc công cụ tạo QR bất kỳ); lưu `figures/4_qr_dashboard.png`; chạy `python scripts/sync_figures.py` để chép sang `report/figures` và `slides/figures`; đặt QR ở slide cuối phần dashboard (do Người 4, slide D8 trong `Nguoi-4.md`) và báo cáo 4.
- [ ] **Thống kê bộ dashboard:** nhận số thật từ Người 4 và cập nhật bảng ở báo cáo 4.1.5 (`report/tables/p8b_dashboard_stats.tex` đang là số thiết kế).

### 7.2 Mở rộng
- [ ] **P9 – thu thập API** (`docs/prompts/P9-thu-thap-api.md`): chạy; lấy `docs/THU_THAP_API.md`, `figures/5-2_*.png`, handoff; điền `5-2-thu-thap-api.tex` (5 `\todo`) và slide mục 5.2 (khung `[P9]` trong `04-mo-rong.tex`).
- [ ] **P10 – Lakehouse** (`docs/prompts/P10-lakehouse.md`): cần Docker Desktop (WSL2) trên máy Windows; lấy `docs/LAKEHOUSE.md`, `figures/5-1_*.png`, handoff; điền `5-1-lakehouse.tex` (4 `\todo`) và slide mục 5.1 (khung `[P10]`). Cấu trúc trình bày: **kiến trúc → triển khai (mỗi bước một slide minh chứng) → kết quả**.
- [ ] **Superset – DB1:** dựng DB1 trên Superset đọc tầng Gold qua Trino; so sánh số với DB1 Power BI; ảnh chụp và slide P7.
- [ ] **Kiến trúc Lakehouse bằng draw.io** (mục 6), có logo công nghệ, vẽ theo lớp.

### 7.3 Slide
- [ ] **Mở đầu** (`00-mo-dau.tex`): bìa, mục lục, "Dự án trong một trang" (số liệu từ `handoff/00-TONG-QUAN.md`); điền tên nhóm, thành viên, giảng viên trong `main.tex` (khối THÔNG TIN CẦN SỬA); phối hợp Người 1 về hai frame lý thuyết (file này có hai người cùng sửa: thống nhất ai sửa frame nào).
- [ ] **Chương 5** theo kiến trúc → triển khai → minh chứng → kết quả (mục 5).
- [ ] **Kết luận** (`05-tong-ket.tex`): số kết quả, 3 bài học chính từ Người 4, hạn chế.
- [ ] **Ghép slide:** nhận `.tex` và hình từ `04_Docs/tex-nop/` (hạn 27/11); chép vào `slides/sections/` và `slides/figures/` (đúng tên file); biên dịch `latexmk -lualatex main.tex`; kiểm tra số trang (hiện 167), không còn khung đỏ (`khungchen`), không còn `[nhóm xác nhận]`; chạy `python scripts/make_slides_zip.py`.
- [ ] **Số liệu cần đồng bộ trước khi ghép:** S78 ghi "20–26 giây", số thật 21,3–27,6 giây (S105 đã ghi 21–28); S90 ghi "16 bảng", mô hình hiện có 38 bảng; S47 "380/842" và các slide dashboard "379" cùng tồn tại (khác phạm vi đơn, có ghi chú); kiểm tra các số khác khi slide đã sửa.

### 7.4 Tổng duyệt (28–29/11)
- [ ] Chạy thử toàn bộ theo thứ tự: Phú → Người 1 → Người 2 → Người 3 → Người 4 → Phú; bấm giờ từng người (giả định ở các file `Nguoi-x.md`); điều chỉnh số slide nói khi có thời lượng chính thức.
- [ ] Chuẩn bị phương án dự phòng: ảnh chụp dashboard nếu mất mạng; slide dự phòng B01–B10 trong `99-du-phong.tex` cho 10 câu vấn đáp dễ gặp.
- [ ] Mỗi người đọc phần câu hỏi trong file của mình (mục 9); Phú đọc mục 9 của file này.

### 7.5 Giai đoạn 2 (sau thuyết trình): báo cáo
- [ ] Nhận file `.tex` báo cáo từ từng người vào `04_Docs/tex-nop/`; chép vào `report/chapters/`; `python scripts/export_latex.py` cập nhật bảng và mã sinh từ database; biên dịch `cd report && latexmk -xelatex main.tex`; đảm bảo > 100 trang (hiện 128 trang); chạy `python scripts/make_overleaf_zip.py`.
- [ ] Viết phần của mình (số trang và `\todo` ở mục 10).

## 8. Việc riêng
Phú không có việc riêng ngoài mục 7; việc dài nhất là P9, P10 và ghép file tổng.

## 9. Câu hỏi có thể bị hỏi

Các câu từ `huong-dan/04-cau-hoi-van-dap.md` thuộc phần này:

<!-- QA:17,18,38,40 -->
**Q17. Vì sao biến đổi bằng SQL procedure thay vì pandas?**
Dữ liệu nằm sẵn trong PostgreSQL, xử lý theo tập hợp (window function, upsert) nhanh và ngắn hơn; Python chỉ điều phối và COPY. Nạp full toàn bộ 1,56 triệu dòng nguồn vào kho mất khoảng 1,5 phút.

**Q18. Dựng lại toàn bộ dự án mất bao lâu và có tái lập không?**
Một lệnh `python scripts/rebuild_all.py --drop` xoá hai database và dựng lại từ CSV: **443 giây (7,4 phút)**; kết quả giống hệt trước khi xoá (16/16 bảng khớp checksum), 130/130 test đạt khi dựng (133 sau khi thêm test địa lý).

**Q38. Những giới hạn của dự án?**
(1) Nạp tăng dần chỉ mô phỏng bản ghi mới với trạng thái cuối, không có đơn đổi trạng thái giữa chừng; (2) cơ chế thử lại mồ côi mới chứng minh bằng test; (3) toạ độ theo mã bưu chính (không phải địa chỉ), haversine là đường chim bay (sai số ≤ 0,5%); (4) dữ liệu 2016 và cuối 2018 thưa; (5) chỉ 45,1% deal có đơn nên so sánh theo kênh nhỏ (kênh Email chỉ 6 seller có đơn, đánh dấu mẫu nhỏ); (6) benchmark gọn trên một laptop.

**Q40. Nếu mở rộng, bạn sẽ làm gì tiếp?**
Thêm trạng thái trung gian của đơn (CDC thật) và lịch chạy tự động; chuyển toạ độ sang PostGIS khi cần truy vấn không gian; phân vùng `fact_order_item` theo năm khi dữ liệu lớn; thêm chiều khuyến mãi/sản phẩm theo thời gian (SCD cho giá); và đo hiệu năng nhiều người dùng đồng thời.
<!-- /QA -->

Câu mới:

**Q-P1. Vì sao lakehouse mà không dùng SQLite hay DuckDB?**
Lakehouse cần lưu trữ dạng object storage cộng table format có ACID (Apache Iceberg: giao dịch, time travel); SQLite hay DuckDB file chỉ là một CSDL trên một máy, không có các đặc tính đó nên không đúng nghĩa lakehouse.

**Q-P2. Lakehouse khác kho PostgreSQL ở đâu và bạn giải quyết giới hạn nào?**
Kho chương 3 nạp theo lô, ghi đè trạng thái của đơn và không giữ dữ liệu thô; lakehouse nhận dữ liệu liên tục qua CDC, giữ lịch sử sự kiện và dữ liệu thô ở Bronze, và tách lưu trữ khỏi tính toán. Gold có cùng star schema nên đối soát được từng con số với kho cũ. Số liệu thật: điền sau P10.

**Q-P3. Dữ liệu API đem lại gì cho kho?**
Dữ liệu Olist là ảnh chụp tĩnh nội bộ; API công khai của Brazil (IBGE, Banco Central, BrasilAPI) bổ sung dân số theo bang, tỷ giá và lạm phát, ngày lễ, để trả lời doanh thu trên đầu người, tăng trưởng thực, GMV quy đổi USD. Số liệu thật: điền sau P9.

**Q-P4. Vì sao thêm Superset khi đã có Power BI?**
Barem khuyến khích công cụ trực quan mới; DB1 dựng lại trên Superset đọc từ tầng Gold của lakehouse cho cùng số liệu với Power BI, chứng minh lớp Gold dùng được cho nhiều công cụ BI.

**Q-P5. Nếu có thêm thời gian, nhóm làm gì tiếp?**
Xem Q40 ở trên: đơn đổi trạng thái giữa chừng, PostGIS cho truy vấn bán kính, lịch chạy tự động, khai phá dữ liệu (phân lớp, phân cụm, luật kết hợp).

## 10. Giai đoạn 2 (sau thuyết trình): viết báo cáo

Số trang hiện tại: <!-- PAGES:5.1,5.2,6.1,6.2,6.3 -->mục 5.1: trang 80 (1 trang); mục 5.2: trang 81 (1 trang); mục 6.1: trang 82 (1 trang); mục 6.2: trang 82 (1 trang); mục 6.3: trang 83 (1 trang); tổng 5 trang<!-- /PAGES -->. Phần `00-*` (bìa, lời mở đầu, đánh giá, từ viết tắt) và phụ lục nằm ngoài mục lục theo số chương.

Các `\todo` hiện có (đếm từ mã nguồn):

<!-- TODOS:00-bia.tex,00-loi-mo-dau.tex,00-danh-gia-thanh-vien.tex,00-tu-danh-gia.tex,00-viet-tat.tex,5-1-lakehouse.tex,5-2-thu-thap-api.tex,06-ket-luan.tex -->
| File | Số `\todo` | Nội dung các `\todo` |
| --- | ---: | --- |
| `report/chapters/00-bia.tex` | 1 | 1. Điền tên giảng viên, lớp, nhóm, thành viên và MSSV ở bìa. |
| `report/chapters/00-loi-mo-dau.tex` | 1 | 1. Viết lời mở đầu (nửa trang đến một trang): bối cảnh (thương mại điện tử, nhu cầu phân tích dữ liệu), mục tiêu của bài tập lớn, phạm vi (hai bộ dữ liệu Olist, PostgreSQL, Power BI), bố cục báo cáo sáu chương, lờ… |
| `report/chapters/00-danh-gia-thanh-vien.tex` | 1 | 1. Trưởng nhóm điền điểm sau khi cả nhóm thống nhất; in ra và ký. Mẫu theo bảng đánh giá thành viên của môn học (5 tiêu chí). |
| `report/chapters/00-tu-danh-gia.tex` | 1 | 1. Nhóm điền cột "Đạt" và ghi chú khi hoàn thiện báo cáo. |
| `report/chapters/00-viet-tat.tex` | 1 | 1. Bổ sung các từ viết tắt khác xuất hiện trong báo cáo. |
| `report/chapters/5-1-lakehouse.tex` | 4 | 1. P10 điền: kiến trúc lakehouse (lớp lưu trữ, định dạng bảng, engine truy vấn, quan hệ với kho PostgreSQL hiện có); nêu lý do chọn công nghệ và so sánh với kho quan hệ.<br>2. P10 điền: các bước dựng lakehouse (nạp dữ liệu nguồn, phân lớp dữ liệu, truy vấn mẫu), kèm mã và lệnh chạy.<br>3. P10 điền: số liệu đo được (số bảng, số dòng, thời gian truy vấn so với PostgreSQL), hình minh hoạ, hạn chế.<br>4. P10 điền: dựng lại dashboard DB1 (tổng quan và doanh thu) trên Apache Superset, đọc tầng Gold của lakehouse qua Trino; so sánh với DB1 trên Power BI (cùng số liệu, khác công cụ); ảnh chụp figures/5-1_superset_d… |
| `report/chapters/5-2-thu-thap-api.tex` | 5 | 1. P9 điền: dữ liệu Olist là ảnh chụp tĩnh; bài toán là bổ sung dữ liệu thực tế (nguồn API nào, bổ sung cho câu hỏi phân tích nào của chương 2).<br>2. P9 điền: sơ đồ luồng từ API đến staging, tần suất gọi, xử lý lỗi và giới hạn tốc độ; nối với kiến trúc các lớp ở mục sec:kien-truc.<br>3. P9 điền: mã thu thập (Python), lược đồ bảng đích, lịch chạy, cách đưa vào pipeline.<br>4. P9 điền: số dòng thu được, ví dụ phân tích dùng dữ liệu mới, hạn chế.<br>5. P9 điền: dashboard D8 (thị trường Brazil, dữ liệu API) thuộc chương 5, dựng bằng Power BI từ dữ liệu thu thập qua API; hướng dẫn ở huong-dan/dashboards/D8.md; ảnh chụp đặt tên theo quy ước của chương 5. |
| `report/chapters/06-ket-luan.tex` | 3 | 1. Viết lại bằng lời của nhóm. Gợi ý các ý đã có số liệu: kho dữ liệu hình sao với 10 bảng chiều và 6 bảng fact thuộc cả ba loại; hai hệ thống nguồn và 1,56 triệu dòng; pipeline chạy lại từ đầu bằng một lệnh trong…<br>2. Nhóm bổ sung bài học về làm việc nhóm, phân công, công cụ (Git, Power BI) và khó khăn thực tế.<br>3. Chỉnh danh sách hạn chế theo thực tế sau khi dựng dashboard. |
| **Tổng** | **17** | |
<!-- /TODOS -->

## 11. Mốc hạn

| Hạn | Việc | Xong |
| --- | --- | --- |
| 23/11 | Kiến trúc Lakehouse (draw.io, nếu đã có thiết kế P10); slide mở đầu | ☐ |
| 25/11 | File gốc `olist_base.pbix` và zip đã lên Drive từ trước; nhận bản đầu dashboard của mọi người | ☐ |
| 26/11 | Nhận bài học từ Người 4 (đã gom) | ☐ |
| 27/11 | Slide và dashboard xong: ghép slide và file tổng; publish, QR | ☐ |
| 28–29/11 | Tập, bấm giờ, tổng duyệt | ☐ |
| Tuần 12 | Thuyết trình | ☐ |
