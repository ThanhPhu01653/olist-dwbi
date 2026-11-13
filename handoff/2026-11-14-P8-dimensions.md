# P8-E3 – Hệ thống chiều khái niệm (số liệu từ olist_dw)

*Sinh tự động bởi `scripts/p8_dimensions.py`.*

## Chiều thời gian: Năm → Quý → Tháng → Ngày

| Năm | Quý | Tháng | Ngày |
| --- | --- | --- | --- |
| 2016 | 2016-Q4 | 2016-12 | 2016-12-25 |
| 2017 | 2017-Q4 | 2017-11 | 2017-11-24 |
| 2018 | 2018-Q1 | 2018-03 | 2018-03-15 |
| **5** | **20** | **60** | **1.827** |

(dòng cuối: số giá trị phân biệt của từng cấp)

## Chiều địa lý: Vùng → Bang → Thành phố → Mã bưu chính

| Vùng | Bang | Thành phố (kèm bang) | Mã bưu chính |
| --- | --- | --- | --- |
| Nordeste | BA | salvador | 40010 |
| Sul | RS | porto alegre | 90001 |
| Sudeste | SP | sao paulo | 01001 |
| **5** | **27** | **6.190** | **19.177** |

(dòng cuối: số giá trị phân biệt của từng cấp)

## Chiều sản phẩm: Nhóm ngành → Danh mục → Sản phẩm

| Nhóm ngành hàng | Danh mục (tiếng Anh) | Sản phẩm (product_id) |
| --- | --- | --- |
| Electronics & Computers | computers_accessories | 0021a87d |
| Health & Beauty | health_beauty | 00210e41 |
| Home & Furniture | bed_bath_table | 0009406f |
| **13** | **74** | **32.951** |

(dòng cuối: số giá trị phân biệt của từng cấp)

## Chiều seller: Vùng → Bang → Thành phố → Seller

| Vùng | Bang | Thành phố (kèm bang) | Seller |
| --- | --- | --- | --- |
| Sudeste | MG | belo horizonte | 00d8b143 |
| Sul | PR | curitiba | 01266d4c |
| Sudeste | SP | sao paulo | 00ab3eff |
| **6** | **23** | **636** | **3.557** |

(dòng cuối: số giá trị phân biệt của từng cấp)

## Chiều khách hàng (SCD loại 2): Vùng → Bang → Thành phố → Mã bưu chính → Khách → Phiên bản

| Vùng | Bang | Thành phố (kèm bang) | Mã bưu chính | Khách thật | Phiên bản (dòng) |
| --- | --- | --- | --- | --- | --- |
| Sudeste | MG | belo horizonte | 31555 | 000c8bdb | 1 |
| Sudeste | RJ | rio de janeiro | 21380 | 00293787 | 1 |
| Sudeste | SP | sao paulo | 03071 | 001a2bf0 | 1 |
| **5** | **27** | **4.310** | **14.994** | **96.096** | **96.338** |

(dòng cuối: số giá trị phân biệt của từng cấp)

## Chiều kênh thu hút: Nhóm kênh → Origin

| Nhóm kênh | Origin |
| --- | --- |
| Email | email |
| Organic | direct_traffic |
| Other | other |
| **6** | **10** |

(dòng cuối: số giá trị phân biệt của từng cấp)

## Chiều trạng thái đơn: Nhóm trạng thái → Trạng thái

| Nhóm trạng thái | Trạng thái đơn |
| --- | --- |
| Completed | delivered |
| Failed | canceled |
| In progress | approved |
| **3** | **8** |

(dòng cuối: số giá trị phân biệt của từng cấp)

## Chiều hình thức thanh toán: Nhóm → Hình thức

| Nhóm thanh toán | Hình thức |
| --- | --- |
| Bank slip | boleto |
| Card | credit_card |
| Unknown | not_defined |
| Voucher | voucher |
| **4** | **5** |

(dòng cuối: số giá trị phân biệt của từng cấp)

## Chiều nhân viên sales: Vai trò → Nhân viên

| Vai trò | Nhân viên |
| --- | --- |
| SDR | 068066e2 |
| SR | 060c0a26 |
| **2** | **54** |

(dòng cuối: số giá trị phân biệt của từng cấp)

## Kiểm tra phân cấp

| Phân cấp | Kết quả đếm | Kết luận |
| --- | --- | --- |
| Tháng phải đi kèm năm | chỉ có 12 số tháng nhưng 60 cặp (năm, tháng): tên tháng một mình không xác định một nút của phân cấp | đúng: dùng year_month ('YYYY-MM') và year_quarter làm cấp, không dùng month một mình |
| Thành phố phải đi kèm bang | 5.814 tên thành phố nhưng 6.190 cặp (bang, thành phố); 303 tên thành phố xuất hiện ở từ 2 bang trở lên (nhiều nhất: bom jesus (6 bang), sao domingos (6 bang), boa esperanca (5 bang)) | đúng: cấp thành phố luôn đi kèm bang; không gộp theo tên thành phố |
| Mã bưu chính xác định một thành phố và một bang | 0 mã có nhiều hơn một thành phố, 0 mã có nhiều hơn một bang | đúng: dim_geography có một dòng cho mỗi mã bưu chính |
| Bang thuộc đúng một vùng | 0 bang thuộc nhiều hơn một vùng (27 bang, 5 vùng) | đúng: Vùng → Bang là quan hệ một nhiều |
| Sản phẩm → danh mục → nhóm ngành | 0 danh mục thuộc nhiều hơn một nhóm ngành (74 danh mục, 13 nhóm ngành) | đúng: mỗi danh mục một nhóm; sản phẩm chưa có danh mục vào nhóm unknown |
| Origin → nhóm kênh | 0 origin thuộc nhiều hơn một nhóm kênh (10 origin, 6 nhóm kênh) | đúng: mỗi origin một nhóm kênh |

## Phân nhóm dimension

| Nhóm | Chiều | Số dòng | Số fact | Ghi chú |
| --- | --- | ---: | ---: | --- |
| Chiều dùng chung (conformed) | dim_date | 1.828 | 6 | 11 view đóng vai; dùng bởi mọi fact |
| Chiều dùng chung (conformed) | dim_geography | 19.178 | 2 | zip → thành phố → bang → vùng; nối khách, seller |
| Chiều dùng chung (conformed) | dim_seller | 3.558 | 3 | nối quy trình bán hàng với thu hút seller (SCD1) |
| Chiều dùng chung (conformed) | dim_customer | 96.339 | 4 | SCD loại 2: giữ lịch sử mã bưu chính |
| Chiều dùng chung (conformed) | dim_order_status | 9 | 2 | dùng bởi fact đơn hàng và fact xử lý đơn |
| Chiều đóng vai (role-playing) | dim_date | 1.828 | 6 | mua, duyệt, bàn giao, giao, dự kiến, liên hệ, chốt, đơn đầu tiên... |
| Chiều đóng vai (role-playing) | dim_sales_rep | 55 | 1 | một bảng cho hai vai trò: SDR và SR |
| Chiều SCD loại 2 | dim_customer | 96.339 | 4 | đóng phiên bản cũ, mở phiên bản mới khi đổi mã bưu chính |
| Chiều rác (junk) | dim_lead_profile | 503 | 1 | gom 7 thuộc tính nhỏ của deal thành một chiều |
| Danh mục nhỏ (lookup) | dim_order_status | 9 | 2 | trạng thái đơn → nhóm trạng thái |
| Danh mục nhỏ (lookup) | dim_payment_type | 6 | 1 | hình thức thanh toán → nhóm |
| Danh mục nhỏ (lookup) | dim_lead_origin | 11 | 1 | origin → nhóm kênh |
| Chiều của một quy trình (một fact) | dim_product | 32.952 | 1 | sản phẩm → danh mục → nhóm ngành; chỉ fact_order_item dùng |
