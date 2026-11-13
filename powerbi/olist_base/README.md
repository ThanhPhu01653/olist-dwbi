# olist_base – dự án Power BI gốc (định dạng PBIP)

Thư mục này là một **dự án Power BI dạng văn bản** (PBIP) đã dựng sẵn mô hình dữ liệu: 38 bảng (37 bảng từ CSV và bảng chứa measure), 32 quan hệ, 65 measure, 9 cột tính toán, 10 phân cấp, theme và 6 trang báo cáo trống. Mở bằng Power BI Desktop, bấm Refresh, đối chiếu số rồi lưu thành `olist_base.pbix`; từ đó cả nhóm dựng DB1–DB4 trên file `.pbix` đó.

Chưa có visual nào: việc dựng visual do nhóm làm theo `huong-dan/dashboards/DB1.md` … `DB4.md`.

**Chưa mở được trên Power BI Desktop khi sinh dự án này.** Cú pháp được viết theo tài liệu và JSON schema chính thức của Microsoft và đã kiểm tra bằng script (mục 9), nhưng lần mở đầu tiên là lần thử thật. Mục 7 hướng dẫn xử lý khi Power BI báo lỗi.

## 1. Yêu cầu
- **Power BI Desktop trên Windows, bản tháng 6/2025 trở lên** (báo cáo dùng định dạng PBIR phiên bản schema 2.0.0 ra tháng 6/2025; mô hình dùng TMDL, `definition.pbism` phiên bản 4.0). Nên dùng **bản mới nhất** từ Microsoft Store hoặc trang tải Power BI Desktop; các bản mới đọc được định dạng cũ.
- Nếu Power BI Desktop báo không mở được file `.pbip`: vào *File → Options and settings → Options → Preview features* và bật ba mục *Power BI Project (.pbip) save option*, *Store semantic model using TMDL format*, *Store reports using enhanced metadata format (PBIR)* (bản mới có thể không còn các mục này vì đã là mặc định), rồi khởi động lại.
- Thư mục CSV **`01_pBI_data`** (link Google Drive ở `exports/README.md`): chứa 37 file `dim_*.csv`, `fact_*.csv`, `v_*.csv`, `job_run.csv`, `batch_metrics.csv`. Đừng đổi tên file.

## 2. Cấu trúc thư mục
```
powerbi/olist_base/
  olist_base.pbip                      file để mở bằng Power BI Desktop
  olist_base.SemanticModel/            mô hình dữ liệu (TMDL)
    definition.pbism
    definition/
      database.tmdl, model.tmdl        cấu hình chung, thứ tự bảng
      expressions.tmdl                 tham số DataFolder và hàm fnCsv
      relationships.tmdl               32 quan hệ (10 quan hệ inactive)
      tables/*.tmdl                    mỗi bảng một file: cột, phân cấp, truy vấn Power Query
      tables/_Measures.tmdl            65 measure, thư mục hiển thị DB1–DB4
    DAXQueries/kiem_tra_so_lieu.dax    truy vấn kiểm tra số sau Refresh
  olist_base.Report/                   báo cáo (PBIR): 6 trang trống, theme
```
Các file này do `python scripts/gen_pbip.py` sinh từ `powerbi/model.md`, `powerbi/measures.md` và `powerbi/theme.json`; tên bảng, cột, quan hệ, measure lấy từ các tài liệu đó, không gõ tay.

## 3. Mở dự án và đổi `DataFolder`
1. Mở `olist_base.pbip` (bấm đúp, hoặc dùng PowerShell):
   ```powershell
   Start-Process "D:\1 TaiLieuHocTap\Datawarehouse&BI\project\powerbi\olist_base\olist_base.pbip"
   ```
   Lần đầu Power BI mở mô hình **không có dữ liệu** (chưa có bộ nhớ đệm): bình thường.
2. Đổi tham số trỏ tới thư mục CSV trên máy: **Home → Transform data → Edit parameters** (hoặc trong Power Query: **Manage Parameters → DataFolder**), điền đường dẫn thư mục `01_pBI_data`, **không có dấu `\` ở cuối**, ví dụ `D:\Olist\01_pBI_data`. Giá trị mặc định trong dự án là `C:\Olist\01_pBI_data` (chỉ là ví dụ).
   Kiểm tra nhanh đường dẫn bằng PowerShell:
   ```powershell
   Test-Path "D:\Olist\01_pBI_data\dim_date.csv"   # phải ra True
   (Get-ChildItem "D:\Olist\01_pBI_data" -Filter *.csv).Count   # phải ra 37
   ```
3. Bấm **Close & Apply** (nếu đang ở Power Query).

## 4. Refresh
**Home → Refresh.** Lần đầu khoảng 1–3 phút (37 file, khoảng 80 MB) và thêm vài chục giây để tính các cột tính toán. Nếu Power BI hỏi quyền truy cập file hoặc mức riêng tư (*Privacy levels*), chọn *Continue* / *Ignore privacy levels* (dữ liệu cục bộ). Sau khi xong, mỗi bảng có số dòng đúng bằng số dòng CSV (ví dụ `fact_order_fulfillment` 99.441 dòng; `dim_date` 1.827 dòng vì bỏ dòng Unknown `date_key = -1`).

## 5. Kiểm tra số liệu
Cách chính xác nhất là **DAX query view** (biểu tượng DAX query view ở thanh bên trái Power BI Desktop): mở tab `kiem_tra_so_lieu` (nếu không thấy tab, dán nội dung file `olist_base.SemanticModel/DAXQueries/kiem_tra_so_lieu.dax`), chạy từng khối `EVALUATE`; kết quả là số đầy đủ, không bị định dạng K/M. Khối 1 = toàn bộ dữ liệu, khối 2 = cửa sổ 2017-01 → 2018-08 (`dim_date[InWindow] = TRUE`).

Giá trị kỳ vọng (tính bằng SQL trên database; đầy đủ hơn ở `powerbi/measures.md` mục 7):

<!-- EXPECTED:START -->
| Measure | Kỳ vọng: toàn bộ dữ liệu | Kỳ vọng: cửa sổ 2017-01 → 2018-08 | Giá trị thật (ghi lại) |
| --- | ---: | ---: | --- |
| GMV | 13,494,400.74 | 13,449,529.68 | |
| Orders | 98,199 | 97,905 | |
| AOV | 137.42 | 137.37 | |
| Freight ratio | 16.6% | 16.6% | |
| Cancel rate | 1.24% | 1.19% | |
| On-time rate | 93.2% | 93.2% | |
| Avg review | 4.09 | 4.09 | |
| Late rate | 6.8% | 6.8% | |
| % negative | 14.7% | 14.6% | |
| MQLs | 8,000 | 8,000 | |
| Won deals | 842 | 842 | |
| Seller GMV (monthly) | 13,494,400.74 | 13,449,529.68 | |
<!-- EXPECTED:END -->

Nếu số khớp (làm tròn theo cột kỳ vọng) thì mô hình, quan hệ và measure đều đúng. Ghi chú:
- Trên thẻ (card) hoặc bảng, measure tiền và số đơn hiển thị rút gọn theo định dạng của dự án (GMV `13.5M`, Orders `98.2K`); đó là hiển thị, giá trị thật là số đầy đủ ở DAX query view.
- Cùng mô hình, cùng bộ lọc thì số phải khớp từng chữ số vì cột tiền dùng kiểu *Fixed decimal number*.

Kiểm tra thêm trong **Model view**: 32 quan hệ, trong đó 10 quan hệ nét đứt (inactive: ngày giao, ngày hạn bàn giao, địa lý seller, …); `dim_date` có biểu tượng bảng ngày.

## 6. Lưu thành `olist_base.pbix`
Sau khi số khớp: **File → Save as** và chọn loại file **Power BI files (.pbix)**, đặt tên `olist_base.pbix`. Đưa file này lên Google Drive cho cả nhóm. File `.pbix` và bộ nhớ đệm không được commit (đã có trong `.gitignore`: `*.pbix`, `**/.pbi/cache.abf`, `**/.pbi/localSettings.json`).

Sau khi lưu `.pbix`, file đó là bản làm việc; nếu sửa mô hình thì sửa trong `.pbix` (hoặc sửa tài liệu rồi chạy lại `gen_pbip.py` và làm lại các bước trên). Power BI Desktop có thể thêm `lineageTag` và `diagramLayout.json` khi lưu lại dạng PBIP; việc này không ảnh hưởng nội dung.

Nội dung đã dựng sẵn để nhóm biết dùng:
| Thành phần | Chi tiết |
| --- | --- |
| Bảng | 10 `dim_*`, 6 `fact_*`, 15 `v_*` (mart, bảng rời, không có quan hệ), 6 bảng giám sát ETL (`job_run`, `v_run_summary`, `v_dq_summary`, `v_rejected_summary`, `batch_metrics`, `fact_load_issue`), `_Measures` |
| Kiểu dữ liệu | khoá và số đếm: số nguyên; tiền: *Fixed decimal number*; ngày: Date (`YYYY-MM-DD`); zip: văn bản (giữ số 0 đầu); cờ: True/False |
| `dim_date` | bỏ dòng `date_key = -1`; đánh dấu là bảng ngày (cột `full_date`); thêm cột `InWindow` (TRUE cho 2017-01 → 2018-08) dùng làm bộ lọc trang |
| Quan hệ | 32 quan hệ nhiều–một, lọc một chiều; mỗi fact một quan hệ ngày active, còn lại inactive (measure dùng `USERELATIONSHIP`); `dim_sales_rep`: SDR active, SR inactive |
| Phân cấp | Date, Week, Geography (vùng → bang → thành phố → zip), Product (nhóm ngành → danh mục), Seller location, Acquisition, Customer location, Lead origin, Status, Payment |
| Sắp xếp theo cột | `month_name` theo `month`; `day_name` theo `day_of_week`; `delay_bucket` theo `delay_bucket_no`; `stage` theo `stage_no`; `Delay bucket` theo `Delay bucket order` |
| Cột tính toán | `Delay bucket` và `Delay bucket order` trên `fact_order_fulfillment`; 7 cột cho Key Influencers của DB2 trên `fact_review` (`Review type`, `Delay days (order)`, …) |
| Measure | 65 measure trong `_Measures`, thư mục hiển thị: `DB1 Tổng quan và doanh thu`, `DB2 Giao hàng và trải nghiệm khách`, `DB3 Địa lý và phí vận chuyển`, `DB4 Thu hút và hiệu quả seller` (kèm thư mục con), `Cảnh báo màu`, `Giám sát ETL` |
| Định dạng measure | tiền `13.5M` / `998.2K`; số đơn `98.2K`; phần trăm `0.0%`; ngày `0.0` (chuỗi `[>=1000000]#,0.0,,"M";[>=1000]#,0.0,"K";…`) |
| Cột ẩn | mọi cột `*_key`, `etl_batch_id`, `Delay bucket order` |
| Báo cáo | 6 trang trống: DB1, DB2, DB3, *DB3 Chi tiết bang* (drill-through theo `dim_geography[state_code]`), DB4, *DB4 Chi tiết seller* (drill-through theo `dim_seller[seller_id]`); theme `powerbi/theme.json` |

Chưa có sẵn: visual, trang tooltip (`Tooltip_Thang`, …), bookmark, định dạng có điều kiện gắn vào visual, dự báo, Key Influencers. Nhóm dựng theo hướng dẫn DB1–DB4.

## 7. Nếu Power BI báo lỗi khi mở
**Đọc thông báo lỗi.** Lỗi TMDL nêu **tên file và số dòng** (ví dụ `tables/fact_review.tmdl`, line 120). Mở file đó bằng VS Code (có tiện ích *TMDL*), xem dòng được báo, sửa, lưu rồi mở lại. Lỗi ở báo cáo nêu đường dẫn tới file `.json` trong `olist_base.Report/definition/`.

| Hiện tượng | Nguyên nhân thường gặp và cách xử lý |
| --- | --- |
| Không mở được `.pbip` | bản Power BI Desktop quá cũ hoặc chưa bật Preview features (mục 1) |
| Lỗi TMDL khi mở | sửa đúng dòng được báo. Quy tắc: thụt đầu dòng bằng tab; tên có dấu cách đặt trong dấu nháy đơn; giá trị `formatString` đặt trong dấu nháy kép |
| Lỗi ở `pages/.../page.json` | hai trang drill-through (`db3_chi_tiet_bang`, `db4_chi_tiet_seller`) có khối `type`, `filterConfig`, `pageBinding`. Xoá ba khối này trong hai file đó để trang thành trang thường, rồi tự đặt drill-through trong Power BI (*Format page → Page type = Drillthrough*, kéo `state_code` / `seller_id` vào *Drill through*) |
| Lỗi ở `report.json` về theme | xoá khối `themeCollection` và `resourcePackages`, mở lại, rồi nạp theme bằng *View → Themes → Browse for themes* chọn `powerbi/theme.json` |
| `DataSource.NotFound` khi Refresh | `DataFolder` sai hoặc có dấu `\` ở cuối (mục 3) |
| Tên cột đầu tiên hiện `ï»¿...` hoặc Refresh báo thiếu cột | file CSV không phải UTF-8 có BOM theo quy ước; tải lại thư mục CSV từ Drive |
| *We couldn't convert to Number / Date* ở một bảng | CSV khác định dạng với `powerbi/model.md` (phụ lục): xem bảng và cột được báo, sửa kiểu ở bước `fnCsv(...)` của bảng đó (Transform data → Advanced editor) |
| Bảng giám sát ETL lỗi cột thời gian | các cột `started_at`, `finished_at`, … được cắt 19 ký tự đầu rồi đổi sang datetime; nếu lỗi, các bảng này không dùng cho DB1–DB4 nên có thể bỏ khỏi mô hình |
| Cột tính toán `LOOKUPVALUE` báo lỗi hoặc chạy rất chậm | các cột của DB2 trang 3 trên `fact_review`; xoá cột và tạo lại theo `powerbi/model.md` mục 8 |
| Số lệch kỳ vọng | đang bật `InWindow`; hoặc quan hệ nào đó sai kiểu (xem Model view); so với cột đúng của bảng kỳ vọng |

**Dự phòng: dựng tay.** Nếu dự án PBIP không dùng được, tạo file mới và làm theo `powerbi/model.md`: mục 2 (tham số `DataFolder`, hàm `fnCsv`), mục 3 (nạp bảng từ Phụ lục, xử lý riêng `dim_date`), mục 4 (32 quan hệ), mục 5 (bảng ngày, sắp xếp, cột tính toán), mục 6 (phân cấp), rồi `powerbi/measures.md` (measure). Toàn bộ nội dung của dự án này lấy từ các mục đó nên kết quả giống nhau (chỉ khác kiểu cột tiền: dự án này dùng *Fixed decimal number*, tài liệu tay dùng *Decimal number*; số vẫn khớp kỳ vọng).

## 8. Sinh lại dự án
```powershell
python scripts/gen_pbip.py            # sinh lại và kiểm tra (đọc exports/powerbi nếu có)
python scripts/gen_pbip.py --no-csv   # bỏ bước kiểm tra CSV
```
Lệnh này **ghi đè** hai thư mục `olist_base.SemanticModel` và `olist_base.Report`: chỉ chạy khi chưa có ai chỉnh dự án bằng tay (sau khi lưu `.pbix`, bản gốc là file `.pbix`).

## 9. Đã kiểm tra những gì (không cần Power BI)
`gen_pbip.py` kiểm tra sau khi sinh:
- mọi `bảng[cột]` và `[measure]` trong 65 measure và 9 cột tính toán đều tồn tại trong mô hình;
- 32 quan hệ: hai đầu cùng kiểu dữ liệu; mỗi cặp bảng chỉ có một quan hệ active; cột phía "một" không trùng và không rỗng; không dòng nào của bảng fact thiếu khoá ở phía "một" (ngoài giá trị `-1` / rỗng, nơi dim đã có dòng Unknown hoặc đã bỏ có chủ đích);
- 37 file CSV trong `exports/powerbi/`: tên cột khớp, mọi giá trị đúng kiểu đã khai báo (số nguyên, số, ngày, ngày giờ, đúng/sai);
- phân cấp và cột sắp xếp trỏ tới cột có thật;
- các file JSON (`.pbip`, `.pbism`, `.pbir`, `.platform`, `report.json`, `page.json`, `pages.json`, `version.json`) hợp lệ với JSON schema công bố của Microsoft.
