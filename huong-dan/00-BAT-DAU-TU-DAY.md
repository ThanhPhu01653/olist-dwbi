# 00 – Bắt đầu từ đây

*Bộ tài liệu dùng chung cho cả nhóm. Không cần cài gì để đọc: mở trên GitHub là xem được cả bảng và hình. Mọi số liệu lấy từ truy vấn thật trên kho dữ liệu `olist_dw` ở trạng thái cuối (99.441 đơn, GMV 13,49 triệu BRL).*

## 1. Dự án trong 5 dòng
1. Dữ liệu: 2 bộ Kaggle của Olist (bán hàng 99.441 đơn + marketing 8.000 MQL) → 11 file CSV.
2. Chúng ta đã xây **kho dữ liệu** PostgreSQL (nguồn → staging → ODS → kho hình sao → data mart), nạp tăng dần 11 đợt, 133 phép kiểm thử đạt.
3. Kho xuất ra **37 file CSV** (`exports/powerbi/`, chia sẻ qua Google Drive) để dựng **7 dashboard Power BI**.
4. Việc còn lại của cả nhóm: **dựng dashboard, vẽ lại sơ đồ, viết báo cáo (> 100 trang), làm slide (> 100 trang)**; báo cáo trước lớp tuần 12 (30/11–6/12/2026).
5. Trang tổng quan đầy đủ: [`handoff/00-TONG-QUAN.md`](../handoff/00-TONG-QUAN.md).

## 2. Chọn lộ trình theo công việc
Thời gian là thời gian **đọc** (chưa tính thời gian làm).

### A. Dựng dashboard Power BI
| Thứ tự | Đọc file | Để làm gì | Khoảng |
| ---: | --- | --- | ---: |
| 1 | [`handoff/00-TONG-QUAN.md`](../handoff/00-TONG-QUAN.md) mục 1–5 | hiểu dự án, các bảng, KPI | 15 phút |
| 2 | [`02-thuat-ngu.md`](02-thuat-ngu.md) (lướt mục A, B, E) | hiểu fact, dimension, role-playing, DAX | 15 phút |
| 3 | [`powerbi/model.md`](../powerbi/model.md) mục 1–7 | **làm theo từng bước**: tham số `DataFolder`, nạp bảng, quan hệ, phân cấp | 40 phút đọc + 1–2 giờ làm |
| 4 | [`powerbi/measures.md`](../powerbi/measures.md) | copy-paste measure, rồi **đối chiếu bảng giá trị kỳ vọng** ở cuối file | 30 phút đọc + 1 giờ làm |
| 5 | [`dashboards/D1.md`](dashboards/D1.md) | bố cục, slicer, định dạng có điều kiện, số kỳ vọng của D1 | 15 phút |
| 6 | Dựng D1, so số với mục 9 của D1.md. **Chỉ khi D1 khớp số mới sang bước 7** | | |
| 7 | [`dashboards/D2.md`](dashboards/D2.md) … [`D7.md`](dashboards/D7.md) (mỗi dashboard một file) | chia nhau dựng | 10–15 phút mỗi file |
| 8 | [`03-tu-dien-du-lieu.md`](03-tu-dien-du-lieu.md) | tra cột/bảng khi cần (không cần đọc hết) | tra cứu |
| 9 | [`powerbi/model.md`](../powerbi/model.md) mục 9 | Publish to web | 10 phút |

### B. Viết báo cáo
| Thứ tự | Đọc file | Để làm gì | Khoảng |
| ---: | --- | --- | ---: |
| 1 | [`handoff/00-TONG-QUAN.md`](../handoff/00-TONG-QUAN.md) | toàn cảnh, 7 phát hiện, **bảng "Mục báo cáo → file nguồn → hình"** | 25 phút |
| 2 | [`01-pipeline-bang-loi.md`](01-pipeline-bang-loi.md) | hiểu dữ liệu đi qua từng lớp bằng ví dụ thật | 25 phút |
| 3 | [`02-thuat-ngu.md`](02-thuat-ngu.md) | thuật ngữ thống nhất (dùng đúng khi viết) | 20 phút |
| 4 | [`05-nghiep-vu-nhap.md`](05-nghiep-vu-nhap.md) | viết mục 3.1, 3.2.1–3.2.2 (nghiệp vụ, BPMN, canvas) – **bản nháp cần sửa** | 20 phút |
| 5 | Các file `handoff/2026-11-05-P*.md` theo bảng mục báo cáo: mỗi file có **đoạn nháp tiếng Việt** sẵn | viết từng mục | 10–15 phút mỗi file |
| 6 | [`dashboards/D1.md` … `D7.md`](dashboards/) mục "Insight gợi ý" | viết mục phân tích dashboard | 5 phút mỗi file |
| 7 | [`04-cau-hoi-van-dap.md`](04-cau-hoi-van-dap.md) | kiểm tra bài viết đã trả lời được 40 câu | 30 phút |
| 8 | [`03-tu-dien-du-lieu.md`](03-tu-dien-du-lieu.md) | bảng mô tả cột cho phụ lục | tra cứu |

### C. Làm slide
| Thứ tự | Đọc file | Để làm gì | Khoảng |
| ---: | --- | --- | ---: |
| 1 | [`handoff/00-TONG-QUAN.md`](../handoff/00-TONG-QUAN.md) mục 1, 2, 5, 6, 8 | thông điệp chính, KPI, hình | 15 phút |
| 2 | Mục **"Gợi ý slide"** trong từng `handoff/2026-11-05-P*.md` (P0 → P7) | khung slide từng phần (2–4 slide mỗi phase) | 5 phút mỗi file |
| 3 | [`dashboards/D1.md` … `D7.md`](dashboards/) mục "Insight gợi ý" | nội dung slide dashboard | 5 phút mỗi file |
| 4 | [`04-cau-hoi-van-dap.md`](04-cau-hoi-van-dap.md) | chuẩn bị trả lời khi bảo vệ | 30 phút |
| 5 | Thư mục [`figures/`](../figures/) và [`docs/diagrams/`](../docs/diagrams/) | hình có sẵn; sơ đồ cần vẽ lại | 15 phút |

### D. Hiểu pipeline và dữ liệu
| Thứ tự | Đọc file | Để làm gì | Khoảng |
| ---: | --- | --- | ---: |
| 1 | [`01-pipeline-bang-loi.md`](01-pipeline-bang-loi.md) | các lớp nguồn → staging → ODS → kho → mart → Power BI, đi theo một đơn hàng và một MQL thật | 25 phút |
| 2 | [`02-thuat-ngu.md`](02-thuat-ngu.md) | thuật ngữ (grain, SCD, role-playing, materialized view…) kèm ví dụ trong dự án | 20 phút |
| 3 | [`handoff/2026-11-05-P2.md`](../handoff/2026-11-05-P2.md) đến [`P5.md`](../handoff/2026-11-05-P5.md) | làm sạch ODS, dimension, fact, nạp tăng dần | 10–15 phút mỗi file |
| 4 | [`03-tu-dien-du-lieu.md`](03-tu-dien-du-lieu.md) | tra từng bảng và cột của kho | tra cứu |
| 5 | [`04-cau-hoi-van-dap.md`](04-cau-hoi-van-dap.md) | kiểm tra mức hiểu bằng 40 câu hỏi đáp | 30 phút |

## 3. Các file trong `huong-dan/`
| File | Nội dung |
| --- | --- |
| [`00-BAT-DAU-TU-DAY.md`](00-BAT-DAU-TU-DAY.md) | file này |
| [`01-pipeline-bang-loi.md`](01-pipeline-bang-loi.md) | giải thích các lớp; đi theo **một đơn hàng thật** và **một MQL thật** qua từng bảng |
| [`02-thuat-ngu.md`](02-thuat-ngu.md) | thuật ngữ DW/BI, mỗi thuật ngữ có ví dụ ngay trong dự án |
| [`03-tu-dien-du-lieu.md`](03-tu-dien-du-lieu.md) | từ điển mọi bảng `dw` và `mart_*` (sinh tự động): grain, số dòng, từng cột |
| [`04-cau-hoi-van-dap.md`](04-cau-hoi-van-dap.md) | 40 câu giảng viên có thể hỏi + trả lời có số liệu |
| [`05-nghiep-vu-nhap.md`](05-nghiep-vu-nhap.md) | **bản nháp** BPMN, Business Model Canvas, cây nghiệp vụ / yêu cầu / phân tích |
| [`dashboards/D1.md` … `D7.md`](dashboards/) | hướng dẫn dựng từng dashboard: mục tiêu, bố cục lưới, slicer, DAX, số kỳ vọng, insight, checklist giảng viên |

## 3b. Báo cáo LaTeX và kịch bản slide
| File | Nội dung |
| --- | --- |
| [`../report/README.md`](../report/README.md) | **Khung báo cáo LaTeX** (XeLaTeX, 87 trang khung, đã biên dịch được): mỗi mục một file trong `report/chapters/`, việc còn lại đánh dấu `	odo{}` (khung cam); cách lên Overleaf và cách nhiều người gửi file `.tex` cho một người ghép lại |
| [`../slides/slide-script.md`](../slides/slide-script.md) | **Kịch bản 114 slide** chia 7 phần (tiêu đề là câu kết luận có số, hình, ghi chú người nói; dùng được cho PowerPoint và Beamer) + 10 câu vấn đáp dễ gặp kèm slide dự phòng |

Viết báo cáo: sau bước 1–4 ở lộ trình B, mở `report/README.md` và chọn mục cần viết. Làm slide: dùng `slides/slide-script.md` làm dàn bài và `slides/README.md` để biên dịch bộ Beamer; hình lấy trong `figures/`.

## 4. Sơ đồ draw.io (mở và chỉnh)
Ba file trong [`docs/diagrams/`](../docs/diagrams/): `kien-truc-cac-lop.drawio`, `data-model-theo-mart.drawio` (fact màu cam, dimension màu xanh, khung = data mart), `pipeline-etl.drawio`. Bố cục cố ý đơn giản để nhóm chỉnh.
- **Mở**: vào <https://app.diagrams.net> → *File → Open from → Device* → chọn file `.drawio` (hoặc cài app draw.io Desktop, hoặc extension "Draw.io Integration" trong VS Code rồi bấm đúp file).
- **Chỉnh**: kéo thả hình, bấm đúp để sửa chữ, kéo đầu mũi tên để nối lại, đổi màu ở khung *Style* bên phải. Mỗi ô là một hình độc lập.
- **Xuất cho báo cáo**: *File → Export as → PNG*, đặt **Zoom 200%**, bỏ chọn *Transparent background*, lưu vào `figures/` với tên đúng quy ước (ví dụ `3-3-4_data_model_mart.png`).
- Ngoài ra có hình nháp tự động trong `figures/` (`3-3-4_constellation.png`, `3-4-1_pipeline.png`, `3-2-1_bpmn_don_hang.png`…) để xem trước khi vẽ lại.

## 5. Quy ước và mẹo
- **GMV = 13,49 triệu BRL** (không tính đơn hủy); tổng giá hàng mọi đơn là 13,59 triệu. Luôn nói rõ đang dùng số nào.
- Số liệu và hình trong hướng dẫn được **sinh từ database** bằng script (xem mục 6) nên đúng với dữ liệu hiện tại; đừng tự gõ lại số, hãy copy từ file.
- Gặp số lệch hoặc chỗ khó hiểu: ghi lại (file, mục, hiện tượng) và báo KT1 để sửa tài liệu hoặc kiểm tra lại dữ liệu.
- Các file đánh dấu **BẢN NHÁP** (`05-nghiep-vu-nhap.md`, các hình `3-2-*`) cần nhóm đọc, sửa và vẽ lại; không đưa nguyên vào báo cáo.

## 6. Sinh lại tài liệu (cần truy cập database)
| Lệnh | Sinh ra |
| --- | --- |
| `python scripts/gen_trace_examples.py` | khối "đơn hàng thật" và "MQL thật" trong `01-pipeline-bang-loi.md` |
| `python scripts/gen_data_dictionary.py` | `03-tu-dien-du-lieu.md` |
| `python scripts/gen_dashboard_docs.py` | `dashboards/D1.md … D7.md` (số kỳ vọng lấy từ `powerbi/measures.md`; chạy `python scripts/gen_powerbi_docs.py` trước nếu dữ liệu đổi) |
| `python scripts/render_mermaid.py` | hình `figures/3-2-*.png` từ các khối Mermaid trong `05-nghiep-vu-nhap.md` (qua dịch vụ mermaid.ink) |
| `python scripts/gen_bmc.py` | `figures/3-2-3_business_model_canvas.png` |
| `python scripts/gen_drawio.py` | ba file `docs/diagrams/*.drawio` |
| `python scripts/export_latex.py` | bảng số liệu và đoạn SQL/DAX của báo cáo LaTeX (`report/tables/`, `report/code/`) |
| `python scripts/make_overleaf_zip.py` | `report_overleaf.zip` để tải lên Overleaf (không commit) |

## 7. Trạng thái soạn tài liệu
Đã xong: 00, 01, 02, 03, 04, 05, `dashboards/D1–D7`, ba sơ đồ draw.io, hình `3-2-*`, liên kết trong `README.md` và `handoff/00-TONG-QUAN.md`. Chưa làm: kiểm tra tài liệu bằng cách dựng thật trên Power BI Desktop (chưa ai chạy), nên các bước ở `powerbi/model.md` và bố cục ở `dashboards/*.md` có thể cần chỉnh nhỏ khi dựng lần đầu.
