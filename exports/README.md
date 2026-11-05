# Dữ liệu xuất cho Power BI – cách lấy

Bộ CSV đủ dữ liệu (đến 11/2018) nặng khoảng **69 MB** (> 50 MB) nên **không đưa lên GitHub** (`exports/powerbi/*.csv` nằm trong `.gitignore`).
Cả thư mục `exports/powerbi/` được chia sẻ qua Google Drive:

**Link Google Drive:** _(KT1 dán link vào đây sau khi tải thư mục lên)_

Cách dùng:
1. Tải cả thư mục `powerbi` từ link trên về máy (giữ nguyên tên file, không đổi tên).
2. Trong Power BI Desktop chọn nguồn là thư mục đó (hoặc từng file CSV, *File origin* = UTF-8). Danh sách file, cột, khoá nối: `exports/powerbi/README.md` (file này có trong git).
3. Mỗi lần KT1 chạy lại pipeline và tải lại thư mục, **tên file không đổi** nên chỉ cần bấm **Refresh** trong Power BI, không phải dựng lại mô hình.

Người chạy pipeline (KT1): `python scripts/export_powerbi.py` (hoặc `python -m etl.run_pipeline --mode incremental`, bước cuối tự xuất) ghi lại toàn bộ `exports/powerbi/`.
