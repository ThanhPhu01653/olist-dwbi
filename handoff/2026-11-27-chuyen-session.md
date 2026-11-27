# Chuyển session – 2026-11-27

## Trạng thái repo
- `main` đã push, commit cuối trước đợt dọn này: `962869e` (merge P12g); commit dọn nằm ngay sau đó (xem `git log -1`). Không còn nhánh dở (mọi nhánh `phase/P*` đã merge).
- Đã commit trong đợt dọn: `huong-dan/dashboards/D8.md` (D8 khuôn 5 card + 6 biểu đồ, Phú đã duyệt), `docs/prompts/P12*.md`, `docs/prompts/P13-slide-pptx.md`, `slides-pptx/template/` (template pptx, file mẫu, `layout_spec.json`, `build.js`, `make_shapes.py`, `fix_names.py`, `apply_theme.js`, `assets/`).
- Đã restore (không commit): 64 file `powerbi/olist_base/` do Power BI Desktop tự lưu đè; diff chỉ là `lineageTag`, dấu ngoặc `formatString`, xuống dòng, `compatibilityLevel`, đường dẫn tham số `DataFolder`, annotation DevMode, ordinal cột.
- Đã xoá file đo tạm `slides/_sau_p12d.json`, `slides/_truoc_p12d.json`.
- Chưa commit, còn lại trong thư mục làm việc:
  - `powerbi/olist_base.pbip`, `powerbi/olist_base/bak-olist_base.pbip`, `powerbi/icon/`, `powerbi/olist_base/olist_base.SemanticModel/.pbi/`, `.../DAXQueries/.pbi/`, `.../diagramLayout.json`: file Power BI Desktop tạo ra (bản sao, cache, bố cục sơ đồ, icon); chưa duyệt nên không commit.
  - `.pbix` không commit (`*.pbix` đã trong `.gitignore`); `attach/`, `.env` cũng bị ignore.

## Prompt đã chạy (P8 → P12g)
- P8: EDA bổ sung, sơ đồ draw.io nháp, từ điển dữ liệu, bảng và hình theo barem; P8b: tài liệu dashboard DB1–DB4 (`huong-dan/dashboards/`); P8c: dự án PBIP sinh sẵn (`gen_pbip.py`); P8d: hướng dẫn cá nhân từng người.
- P9: thu thập API công khai (IBGE, Banco Central, BrasilAPI, Open-Meteo) vào kho, mart_market, chương 5.2.
- P10: lakehouse (Postgres → Debezium/Kafka → Spark → Iceberg/MinIO → dbt/Trino) và Superset; đối soát 16/16 bảng.
- P11 (và P11b–f): chuẩn trình bày slide Beamer (`QUY-TAC-TRINH-BAY.md`, `bocuc.sty`, checker), dàn lại slide thành viên.
- P12: slide theo checklist của thầy (tiêu đề = tên mục + kết luận ngắn, 65 ký tự); P12b: gọn bộ chính, frame thừa chuyển sang `99-du-phong.tex`, `\LoTrinh`, mức R10 "slide thưa".
- P12c: kiểm định χ², Theil's U, odds ratio, MCA, ma trận Spearman đánh dấu cặp do định nghĩa (`scripts/eda/p12c_categorical.py`).
- P12d: đo vùng nội dung trên PDF, hình to hơn, `slide_fig.py` (chữ ≥ 9 pt sau khi chèn), `kiem_tra_slide.py --pdf`.
- P12e: vẽ lại ~25 sơ đồ ở khổ chèn (`p12e_canvas.py`, `p12e_model.py`, `p12e_drafts.py`).
- P12f: mỗi dashboard một slide khung chờ "ảnh chụp cả trang" (DB3, DB4 giữ khung drill-through).
- P12g: zip Overleaf ≤ 175 file, zip theo người, chế độ nháp `\NHAP`, `ghep_tex_nop.py`.
- **P13 (slide pptx) chưa chạy.**

## Quy ước đang dùng
- Bộ Beamer giữ nguyên trong `slides/` nhưng **không dùng để thuyết trình nữa**; slide mới là pptx theo `docs/prompts/P13-slide-pptx.md` và `slides-pptx/template/`.
- `scripts/kiem_tra_slide.py` (`--strict`, `--pdf slides/main.pdf`, `--anh PDF a-b`): quy tắc R1–R10, chữ trong hình ≥ 9 pt.
- `scripts/slide_fig.py` (`--run`, `--all`): mọi biểu đồ cho slide vẽ qua đây, ra `figures/slide/`; hình báo cáo giữ ở `figures/`.
- `scripts/gen_pbip.py`: measure dùng định dạng `#,0`; sinh `powerbi/olist_base/` từ `powerbi/model.md`, `measures.md`.
- `scripts/make_slides_zip.py`: zip đầy đủ và zip từng người (theme ở gốc zip, tối đa 175 file); `make_overleaf_zip.py` cho báo cáo.
- Không sửa `huong-dan/` khi chưa được duyệt; handoff và tài liệu tiếng Việt, giọng trung lập; số liệu chỉ lấy từ truy vấn thật.

## Lệnh hay dùng (PowerShell trong thư mục dự án)
- Kích hoạt môi trường: `.venv\Scripts\Activate.ps1` (hoặc gọi `.venv\Scripts\python`).
- Pipeline: `python -m etl.run_pipeline --mode full` (thêm `--with-api`, `--no-export`); dựng lại tất cả: `python scripts/rebuild_all.py`.
- Kiểm tra: `python -m etl.run_tests`; slide: `python scripts/kiem_tra_slide.py --strict` và `--pdf slides/main.pdf`.
- Biên dịch: `cd slides; latexmk -lualatex main.tex`; báo cáo: `cd report; latexmk -xelatex main.tex`.
- Zip: `python scripts/make_slides_zip.py`, `python scripts/make_overleaf_zip.py`; đo thời gian zip người: `python scripts/do_thoi_gian_zip.py --nhap`.
- Vẽ lại biểu đồ slide: `python scripts/slide_fig.py --all`, rồi `python scripts/sync_figures.py`.

## Việc còn lại
- Chờ nhóm nộp slide vào `slides-pptx/nop/Nguoi-X`.
- Chạy P13 (dừng sau bước 1 để Phú duyệt).
- Ảnh D8 `4_D8_mot_trang.png` chưa có.
- File ghép Power BI `powerbi/DB_nhom_19_half_done.pbix` đang làm dở.
- Publish to web bị tenant HUST chặn (cần phương án khác cho slide QR).
