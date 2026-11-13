# P8c – Dự án Power BI gốc dạng PBIP

Đọc `CLAUDE.md`, `powerbi/model.md`, `powerbi/measures.md`, `huong-dan/dashboards/README.md` và `DB1.md`–`DB4.md` trước khi làm.

## Bắt đầu
1. Trên `main`, commit `docs/doi-chieu-nhom6.md` và các file mới trong `docs/prompts/`.
2. Tạo nhánh `phase/P8c-pbip`.

## Mục tiêu
Sinh sẵn dự án Power BI dạng PBIP (file văn bản, lưu được vào git). Phú chỉ cần mở bằng Power BI Desktop, bấm Refresh, đối chiếu số rồi lưu thành `olist_base.pbix` cho nhóm dựng DB1–DB4.

## Việc cần làm

### 1. Cấu trúc dự án
- Đặt trong `powerbi/olist_base/` theo cấu trúc PBIP chuẩn:
  - file `.pbip`;
  - thư mục `.SemanticModel` dùng định dạng TMDL;
  - thư mục `.Report`.
- Tra tài liệu chính thức của Microsoft về PBIP và TMDL để viết đúng cú pháp. KHÔNG đoán.
- Ghi vào README phiên bản Power BI Desktop tối thiểu cần dùng.

### 2. Dữ liệu
- Tham số `DataFolder`, kiểu văn bản; giá trị mặc định là đường dẫn ví dụ.
- Mỗi CSV trong `exports/powerbi/` là một bảng; tên bảng = tên file.
- Đọc CSV theo đúng quy ước xuất của dự án: UTF-8 có BOM, dấu phân cách `,`, số thập phân `.`, ngày dạng `YYYY-MM-DD`.
- Đặt đúng kiểu dữ liệu cho từng cột:
  - khoá là số nguyên;
  - tiền là decimal;
  - ngày là date;
  - zip là văn bản (giữ số 0 ở đầu).

### 3. Mô hình
- **`dim_date`:**
  - bỏ dòng `date_key = -1`;
  - đánh dấu là bảng ngày (Mark as date table).
- **Quan hệ:** đủ quan hệ theo `model.md`. Với các ngày role-playing, quan hệ chính là active, các quan hệ còn lại là inactive để measure dùng `USERELATIONSHIP`.
- **Phân cấp và cột:**
  - đủ phân cấp theo `model.md`: năm → quý → tháng → ngày; vùng → bang → thành phố; nhóm ngành → danh mục;
  - đặt sort-by-column cho tên tháng và tên thứ;
  - ẩn các cột khoá.
- **Measure:**
  - toàn bộ measure trong `measures.md`, có format string (K/M, %, số thập phân) và display folder theo DB1–DB4;
  - các measure giám sát ETL đặt trong folder riêng.
- **Key Influencers của DB2:** thêm các cột tính toán như trong `model.md`.
- **Lọc giai đoạn 01/2017 – 08/2018:** dùng cờ `InWindow` như tài liệu đang mô tả.
- **Theme:** dùng `powerbi/theme.json`.

### 4. Report
- 4 trang trống, đặt tên theo DB1–DB4. Thêm các trang drill-through trống: chi tiết bang (DB3) và chi tiết seller (DB4).
- KHÔNG dựng visual; nhóm sẽ tự dựng.

### 5. Không commit
- Dữ liệu cache: `cache.abf`, `localSettings`.
- File `.pbix`.

Thêm các mục này vào `.gitignore`.

### 6. Kiểm tra trước khi giao
Chưa mở được Power BI nên chỉ kiểm tra bằng cách đọc lại:
- Rà từng measure: mọi bảng và cột nhắc tới đều có trong mô hình.
- Rà từng quan hệ: cột hai đầu có cùng kiểu dữ liệu.
- Nếu tìm được công cụ dòng lệnh kiểm tra TMDL thì dùng thêm.

### 7. README
Viết `powerbi/olist_base/README.md` (có bản PowerShell nếu cần), gồm:
- cách mở bằng Power BI Desktop;
- cách đổi `DataFolder` sang thư mục `01_pBI_data` trên máy;
- Refresh;
- kiểm tra số theo bảng giá trị kỳ vọng trong `measures.md` (một bảng ngắn: measure | giá trị kỳ vọng | ô để ghi giá trị thật);
- lưu thành `olist_base.pbix`;
- nếu Power BI báo lỗi khi mở: cách đọc thông báo lỗi, chỗ cần sửa, và cách dựng tay theo `model.md` (dự phòng).

## Kết thúc
- Commit, merge vào `main`, push.
- Viết `handoff/2026-11-14-P8c.md`.

Báo lại cho Phú:
- số bảng, số quan hệ, số measure;
- những gì Phú cần tự kiểm tra khi mở lần đầu;
- những chỗ không chắc chắn về cú pháp.
