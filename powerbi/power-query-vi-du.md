# Ví dụ Power Query: một quy tắc làm sạch viết bằng M

> **Mục đích**: barem yêu cầu ETL dùng nhiều công cụ. Pipeline chính của dự án dùng **SQL** (procedure PostgreSQL) và **Python** (điều phối, nạp, xuất). File này thêm công cụ thứ ba, **Power Query (ngôn ngữ M)**, bằng cách viết lại **cùng một quy tắc làm sạch** và đối chiếu kết quả với hai công cụ kia. Đây là ví dụ minh hoạ trong Power BI Desktop; kho dữ liệu vẫn nạp bằng SQL.

## 1. Quy tắc được viết lại

Quy tắc ở tầng ODS cho bảng toạ độ `geolocation` (xem `docs/mapping.csv`):

| Cột | Quy tắc | SQL (đang dùng ở ODS) |
| --- | --- | --- |
| tên thành phố `geolocation_city` | cắt khoảng trắng, **chữ thường, bỏ dấu** | `lower(unaccent(trim(city)))` |
| mã bưu chính `geolocation_zip_code_prefix` | chỉ giữ chữ số, **đủ 5 ký tự, thêm số 0 đầu** | `lpad(regexp_replace(zip, '[^0-9]', '', 'g'), 5, '0')` |

Lý do cần quy tắc: cùng một thành phố xuất hiện với nhiều cách viết (`são paulo`, `sao paulo`), nên đếm và nối theo tên sẽ sai; mã bưu chính như `01037` bị Power BI tự đoán kiểu và đổi thành số `1037` (mất số 0 đầu) nếu để bước *Changed Type* tự động chạy.

## 2. Mã M (dán vào *Advanced Editor* của một truy vấn trống)

Dùng tham số `DataFolder` đã tạo ở `powerbi/model.md` (đường dẫn thư mục chứa file CSV nguồn; đổi tên file nếu bạn lưu CSV nguồn ở nơi khác).

```m
let
    Nguon = Csv.Document(File.Contents(DataFolder & "olist_geolocation_dataset.csv"),
                [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Header = Table.PromoteHeaders(Nguon, [PromoteAllScalars = true]),
    // Giữ mã bưu chính ở dạng văn bản ngay từ đầu (không để Power BI đổi sang số)
    KieuText = Table.TransformColumnTypes(Header,
                {{"geolocation_zip_code_prefix", type text}, {"geolocation_city", type text}, {"geolocation_state", type text},
                 {"geolocation_lat", type number}, {"geolocation_lng", type number}}, "en-US"),

    // Bảng thay thế ký tự có dấu (chữ thường). Đủ cho mọi ký tự có dấu xuất hiện trong dữ liệu:
    // ã á â à ä é ê è ë í î ì ï ó ô õ ò ö ú ü ù û ç ñ, và º ª (SQL unaccent đổi º thành o)
    BangThayThe = {
        {"ã","a"},{"á","a"},{"â","a"},{"à","a"},{"ä","a"},{"ª","a"},
        {"é","e"},{"ê","e"},{"è","e"},{"ë","e"},
        {"í","i"},{"î","i"},{"ì","i"},{"ï","i"},
        {"ó","o"},{"ô","o"},{"õ","o"},{"ò","o"},{"ö","o"},{"º","o"},
        {"ú","u"},{"ü","u"},{"ù","u"},{"û","u"},
        {"ç","c"},{"ñ","n"}},
    BoDau = (s as nullable text) as nullable text =>
        if s = null then null
        else List.Accumulate(BangThayThe, Text.Lower(Text.Trim(s)), (acc, p) => Text.Replace(acc, p{0}, p{1})),

    // city: chữ thường, bỏ dấu
    SachCity = Table.AddColumn(KieuText, "city_clean", each BoDau([geolocation_city]), type text),
    // zip: chỉ giữ chữ số rồi thêm số 0 đầu cho đủ 5 ký tự
    SachZip = Table.TransformColumns(SachCity,
                {{"geolocation_zip_code_prefix", each Text.PadStart(Text.Select(_, {"0".."9"}), 5, "0"), type text}})
in
    SachZip
```

Kết quả: bảng gốc thêm cột `city_clean`; cột mã bưu chính luôn có 5 ký tự.

## 3. Kết quả mong đợi và đối chiếu ba công cụ

Số đo thật trên bảng `geolocation` (1.000.163 dòng):

| Chỉ số | Trước làm sạch | Sau làm sạch |
| --- | ---: | ---: |
| số tên thành phố khác nhau | 8.011 | 5.968 |
| số dòng có tên thành phố bị đổi | – | 73.440 (SQL, Power Query với bảng thay thế ở trên) |

Ba công cụ cho cùng kết quả:

| Công cụ | Cách viết quy tắc | Dòng đổi | Tên thành phố khác nhau |
| --- | --- | ---: | ---: |
| SQL (ODS) | `lower(unaccent(trim(city)))` | 73.440 | 5.968 |
| Python | chuẩn hoá Unicode NFD, bỏ dấu kết hợp, `lower()`, `strip()` | 73.438 | 5.968 |
| Power Query (M) | bảng thay thế như trên | 73.440 (mong đợi, chưa chạy thật) | 5.968 (mong đợi; kiểm tra bằng *Group By* hoặc *Column distribution*) |

Chênh 2 dòng của bản Python đến từ tên `4º centenario`: ký tự `º` không phân rã trong chuẩn hoá Unicode nên Python giữ nguyên, trong khi `unaccent` của PostgreSQL đổi thành `o`; bảng thay thế M đã thêm `º → o` và `ª → a` để khớp SQL. (Số cột "Power Query" cần **chạy thật trong Power BI để xác nhận**; hai số 73.440 và 5.968 là giá trị mong đợi, tính từ cùng quy tắc.)

Mã bưu chính: trong dữ liệu có 23.995 dòng khách hàng với mã bưu chính bắt đầu bằng số 0 (ví dụ `01037`); nếu để Power Query tự đổi kiểu sang số thì mọi mã này chỉ còn 4 chữ số, và bước `Text.PadStart` ở trên là cách khôi phục.

## 4. Chụp ảnh before/after trong Power BI (để đưa vào báo cáo)

1. **Home → Transform data** mở Power Query Editor. Tạo truy vấn `geolocation_raw` bằng bước `Nguon` đến `KieuText` (chưa làm sạch).
2. Bật **View → Column quality**, **Column distribution**, **Column profile**.
3. Chọn cột `geolocation_city` ở `geolocation_raw`; trong khung *Column profile* nhấn **Value distribution** và chụp ảnh: thấy `são paulo` và `sao paulo` là hai giá trị riêng; ghi lại số *distinct* (8.011).
4. Chọn cột `geolocation_zip_code_prefix`; chụp các mã bắt đầu bằng 0 (nếu để kiểu số sẽ thấy 4 chữ số).
5. **Nhân bản** `geolocation_raw` bằng *Reference* và đặt tên `geolocation_clean`, thêm các bước `SachCity`, `SachZip` như mã ở trên.
6. Chọn cột `city_clean` và chụp lại *Column distribution* (distinct 5.968) và cột zip (đủ 5 ký tự).
7. Ghép hai ảnh cạnh nhau với chú thích "trước (Power Query, 8.011 thành phố)" và "sau (5.968 thành phố)". Đặt tên file `figures/3-3_power_query_before_after.png` (hình này **nhóm chụp từ Power BI**, không sinh tự động).
8. Không bấm **Close & Apply** nếu chỉ minh hoạ (truy vấn này không nằm trong mô hình chính).

## 5. Vị trí trong báo cáo và slide

- Báo cáo mục 3.3 (ETL): bảng "ba công cụ, một quy tắc" ở mục 3 của file này, kèm ảnh before/after.
- Slide: một slide ở phần ETL, tiêu đề dạng "Cùng một quy tắc viết bằng SQL, Python và Power Query cho cùng kết quả: 8.011 → 5.968 thành phố".
