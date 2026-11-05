# Chất lượng dữ liệu nguồn – đếm từng lỗi trong DW_DESIGN §2.3 (olist_full)

*Sinh tự động bởi `scripts/eda/data_quality.py` trên database `olist_full`; chạy lại script để cập nhật số liệu.*

Mỗi dòng: lỗi, số lượng đo được bằng truy vấn, tỷ lệ trên tổng các dòng có thể bị lỗi đó, và cách xử lý ở tầng ODS/DW. Số lượng = 0 nghĩa là đã kiểm tra và không có lỗi ở bản dữ liệu này.

Hình: `figures/3-3-1_data_quality.png`.

## Mã bưu chính

| Bảng | Lỗi | Số lượng | Trên tổng | % | Cách xử lý |
| --- | --- | ---: | ---: | ---: | --- |
| oltp.customers | Zip không đủ 5 chữ số (mất số 0 đầu) – đã kiểm ở P0 | 0 dòng | 99.441 | 0,0% | Không có lỗi ở bản CSV này; ODS vẫn chuẩn hoá char(5) bằng lpad để phòng thủ |
| oltp.sellers | Zip không đủ 5 chữ số (mất số 0 đầu) – đã kiểm ở P0 | 0 dòng | 3.095 | 0,0% | Không có lỗi ở bản CSV này; ODS vẫn chuẩn hoá char(5) bằng lpad để phòng thủ |
| oltp.geolocation | Zip không đủ 5 chữ số (mất số 0 đầu) – đã kiểm ở P0 | 0 dòng | 1.000.163 | 0,0% | Không có lỗi ở bản CSV này; ODS vẫn chuẩn hoá char(5) bằng lpad để phòng thủ |

## Địa lý

| Bảng | Lỗi | Số lượng | Trên tổng | % | Cách xử lý |
| --- | --- | ---: | ---: | ---: | --- |
| oltp.geolocation | Toạ độ nằm ngoài bounding box Brazil | 42 dòng | 1.000.163 | 0,00% | ODS lọc bỏ khỏi phép tính median (không xoá khỏi nguồn) |
| oltp.geolocation | Zip có nhiều hơn 1 toạ độ khác nhau | 17.781 zip | 19.015 | 93,5% | Gom theo zip, lấy median lat/lng (ods.geolocation_zip: 1 dòng / zip) |
| oltp.geolocation | Zip gắn với nhiều hơn 1 bang | 8 zip | 19.015 | 0,04% | Lấy mode (bang phổ biến nhất) của zip |
| oltp.geolocation | Tên thành phố lệch dấu / hoa thường / khoảng trắng | 73.440 dòng | 1.000.163 | 7,3% | Chuẩn hoá lower(unaccent(trim(city))) rồi mới lấy mode |
| oltp.geolocation | Tên thành phố chứa ký tự lạ sau chuẩn hoá (số, dấu *, dấu chấm…) | 1.611 dòng | 1.000.163 | 0,16% | Giữ nguyên, chỉ tính mode; city của zip ưu tiên giá trị phổ biến nhất (thường là tên đúng) |
| oltp.geolocation | Dòng trùng hoàn toàn (cả 5 cột giống nhau) | 261.831 dòng | 1.000.163 | 26,2% | Bị gom khi lấy median/mode theo zip |
| oltp.customers | Tên thành phố lệch dấu / hoa thường | 0 dòng | 99.441 | 0,0% | Chuẩn hoá như trên (nguồn customers đã sạch) |
| oltp.sellers | Tên thành phố lệch dấu / hoa thường | 1 dòng | 3.095 | 0,03% | Chuẩn hoá như trên |
| oltp.customers | Zip không có trong geolocation | 278 dòng | 99.441 | 0,28% | Vẫn tạo dòng dim_geography từ city/state của customer, lat/lng = NULL (xem design-questions.md câu e) |
| oltp.sellers | Zip không có trong geolocation | 7 dòng | 3.095 | 0,23% | Như trên |
| oltp.customers | Bang của khách khác mọi bang xuất hiện trong geolocation của cùng zip | 0 dòng | 99.441 | 0,0% | Ghi nhận; dim_geography lấy bang theo geolocation (mode), bảng customer giữ bang gốc |

## Sản phẩm

| Bảng | Lỗi | Số lượng | Trên tổng | % | Cách xử lý |
| --- | --- | ---: | ---: | ---: | --- |
| oltp.products | Cột sai chính tả *_lenght (product_name_lenght, product_description_lenght) | 2 cột | – | – | Đổi tên thành *_length ở ODS |
| oltp.products | Danh mục rỗng | 610 dòng | 32.951 | 1,9% | Gán 'unknown' |
| oltp.products | Thiếu cân nặng hoặc kích thước | 2 dòng | 32.951 | 0,01% | Giữ NULL + cờ dq_missing_dimensions; size_class = Unknown |
| oltp.products | Cân nặng bằng 0 g (không hợp lý về vật lý) | 4 dòng | 32.951 | 0,01% | Coi như thiếu: giữ nguyên giá trị, gắn cờ; size_class = Unknown |
| oltp.products | Danh mục có trong sản phẩm nhưng không có bản dịch (số danh mục khác nhau) | 2 danh mục | 73 | 2,7% | Bổ sung thủ công qua seeds/category_translation_extra.csv |
| oltp.products | Sản phẩm thuộc danh mục không có bản dịch | 13 dòng | 32.951 | 0,04% | Như trên |

## Đơn hàng

| Bảng | Lỗi | Số lượng | Trên tổng | % | Cách xử lý |
| --- | --- | ---: | ---: | ---: | --- |
| oltp.orders | Trạng thái delivered nhưng không có ngày giao cho khách | 8 dòng | 96.478 | 0,01% | Không xoá đơn; gắn cờ delivered_without_date; delivered_date_key = -1 |
| oltp.orders | Trạng thái delivered nhưng không có ngày bàn giao vận chuyển | 2 dòng | 96.478 | 0,00% | Gắn cờ; handling_days / transit_days = NULL |
| oltp.orders | Trạng thái delivered nhưng không có ngày duyệt | 14 dòng | 96.478 | 0,01% | Gắn cờ; approval_hours = NULL |
| oltp.orders | Có ngày giao khách nhưng trạng thái không phải delivered | 6 dòng | 96.476 | 0,01% | Giữ nguyên trạng thái nguồn, gắn cờ |
| oltp.orders | Ngày duyệt trước ngày mua | 0 đơn | 99.281 | 0,0% | Gắn cờ approved_before_purchase; approval_hours âm → NULL |
| oltp.orders | Ngày bàn giao vận chuyển trước ngày duyệt | 1.359 đơn | 97.644 | 1,4% | Gắn cờ carrier_before_approved; handling_days âm → NULL |
| oltp.orders | Ngày bàn giao vận chuyển trước ngày mua | 166 đơn | 97.658 | 0,17% | Gắn cờ; khoảng thời gian âm → NULL |
| oltp.orders | Ngày giao khách trước ngày bàn giao vận chuyển | 23 đơn | 96.475 | 0,02% | Gắn cờ delivered_before_carrier; transit_days âm → NULL |
| oltp.orders | Ngày giao khách trước ngày mua | 0 đơn | 96.476 | 0,0% | Gắn cờ; lead_days âm → NULL |
| oltp.orders | Ngày giao dự kiến trước ngày mua | 0 đơn | 99.441 | 0,0% | Gắn cờ |
| oltp.orders | Đơn không có dòng hàng nào | 775 dòng | 99.441 | 0,78% | Giữ trong fact_order_fulfillment (item_count = 0); không có trong fact_order_item |
| oltp.orders | Đơn không có dòng thanh toán nào | 1 dòng | 99.441 | 0,00% | Giữ; payment_total = 0 |

## Dòng hàng

| Bảng | Lỗi | Số lượng | Trên tổng | % | Cách xử lý |
| --- | --- | ---: | ---: | ---: | --- |
| oltp.order_items | Hạn giao cho vận chuyển (shipping_limit_date) trước ngày mua | 0 dòng | 112.650 | 0,0% | Ghi nhận; shipping_limit_date_key vẫn nạp |

## Thanh toán

| Bảng | Lỗi | Số lượng | Trên tổng | % | Cách xử lý |
| --- | --- | ---: | ---: | ---: | --- |
| oltp.order_payments | payment_type = not_defined | 3 dòng | 103.886 | 0,00% | Giữ loại not_defined (dim_payment_type có dòng riêng) |
| oltp.order_payments | payment_installments = 0 | 2 dòng | 103.886 | 0,00% | Đổi thành 1 + cờ |
| oltp.order_payments | payment_value = 0 | 9 dòng | 103.886 | 0,01% | Giữ nguyên; ghi nhận |
| oltp.order_payments | Tổng thanh toán lệch tổng (price + freight) của đơn quá 1 BRL | 249 đơn | 98.665 | 0,25% | Không sửa; fact_payment giữ số tiền theo từng lần thanh toán, KPI doanh thu lấy từ price |

## Đánh giá

| Bảng | Lỗi | Số lượng | Trên tổng | % | Cách xử lý |
| --- | --- | ---: | ---: | ---: | --- |
| oltp.order_reviews | review_id xuất hiện ở nhiều hơn 1 dòng (số dòng thừa) | 814 dòng | 99.224 | 0,82% | Khử trùng trên cặp (review_id, order_id), giữ bản có review_answer_timestamp mới nhất |
| oltp.order_reviews | Số review_id bị lặp (số mã khác nhau) | 789 mã | 98.410 | 0,80% | Như trên |
| oltp.order_reviews | Cặp (review_id, order_id) trùng | 0 dòng | 99.224 | 0,0% | Khử trùng (không có ở bản CSV này, PK ghép của oltp đã đảm bảo) |
| oltp.order_reviews | Đơn có nhiều hơn 1 đánh giá | 547 đơn | 98.673 | 0,55% | Giữ cả hai (grain fact_review = cặp review_id, order_id) |
| oltp.order_reviews | Thời điểm trả lời trước thời điểm tạo review | 0 dòng | 99.224 | 0,0% | response_hours âm → NULL |
| oltp.order_reviews | Ngày tạo review trước ngày mua đơn | 74 dòng | 99.224 | 0,07% | Ghi nhận |
| oltp.order_reviews | Không có tiêu đề comment | 87.656 dòng | 99.224 | 88,3% | Giữ NULL; has_comment_title = 0 |
| oltp.order_reviews | Không có nội dung comment | 58.247 dòng | 99.224 | 58,7% | Giữ NULL; has_comment_message = 0 |

## Funnel

| Bảng | Lỗi | Số lượng | Trên tổng | % | Cách xử lý |
| --- | --- | ---: | ---: | ---: | --- |
| crm.mql | origin rỗng | 60 dòng | 8.000 | 0,75% | → 'unknown' |
| crm.closed_deals | business_segment rỗng | 1 dòng | 842 | 0,12% | Cột phân loại → 'unknown' |
| crm.closed_deals | lead_type rỗng | 6 dòng | 842 | 0,71% | Cột phân loại → 'unknown' |
| crm.closed_deals | lead_behaviour_profile rỗng | 177 dòng | 842 | 21,0% | Cột phân loại → 'unknown' |
| crm.closed_deals | business_type rỗng | 10 dòng | 842 | 1,2% | Cột phân loại → 'unknown' |
| crm.closed_deals | has_company rỗng | 779 dòng | 842 | 92,5% | Cột phân loại → 'unknown' |
| crm.closed_deals | has_gtin rỗng | 778 dòng | 842 | 92,4% | Cột phân loại → 'unknown' |
| crm.closed_deals | average_stock rỗng | 776 dòng | 842 | 92,2% | Cột phân loại → 'unknown' |
| crm.closed_deals | declared_product_catalog_size rỗng | 773 dòng | 842 | 91,8% | Giữ NULL (non-additive) |
| crm.closed_deals | declared_monthly_revenue = 0 | 797 dòng | 842 | 94,7% | Giữ số 0, thêm cờ |
| crm.closed_deals | declared_product_catalog_size = 0 | 0 dòng | 842 | 0,0% | Giữ số 0, thêm cờ |
| crm.closed_deals | Ngày chốt (won_date) trước ngày liên hệ đầu (first_contact_date) | 1 dòng | 842 | 0,12% | days_to_close âm → NULL + cờ |
| crm.closed_deals | seller_id của deal không có trong oltp.sellers | 462 deal | 842 | 54,9% | Vẫn tạo dòng dim_seller (địa chỉ Unknown); đây là đặc điểm của 2 hệ thống nguồn, không phải lỗi |

## Chi tiết: nhiều toạ độ cho một zip

19.015 zip trong geolocation; trung bình 52,6 dòng/zip (tối đa 1.146). Chỉ 1.234 zip (6,5%) có đúng 1 toạ độ. Số toạ độ khác nhau mỗi zip: trung vị 22, phân vị 95 là 127, lớn nhất 746. Vì vậy dim_geography phải gom về **1 điểm / zip** (median lat/lng).

## Chi tiết: tên thành phố lệch dấu

geolocation có 8.011 cách viết tên thành phố; sau khi chuẩn hoá `lower(unaccent(trim()))` còn 5.968 (gộp được 2.043 biến thể). Ví dụ tên có dấu bị chuẩn hoá:

| ten_goc | sau_chuan_hoa | so_dong |
| --- | --- | ---: |
| são paulo | sao paulo | 24.918 |
| brasília | brasilia | 2.180 |
| são bernardo do campo | sao bernardo do campo | 1.517 |
| santo andré | santo andre | 1.188 |
| goiânia | goiania | 1.069 |
| niterói | niteroi | 1.029 |

Ví dụ một thành phố có nhiều cách viết trong cùng bang:

| chuan_hoa | bang | cac_cach_viet |
| --- | --- | --- |
| santo estevao | BA | santo estevao \| santo estevão \| santo estêvão |
| sao sebastiao do passe | BA | sao sebastiao do passe \| são sebastião do passe \| são sebastião do passé |
| tome-acu | PA | tome-acu \| tomé-açu \| tomé-açú |
| trairao | PA | trairao \| trairâo \| trairão |
| abadiania | GO | abadiania \| abadiânia |
| abaete | MG | abaete \| abaeté |
| abaira | BA | abaira \| abaíra |
| abare | BA | abare \| abaré |

## Chi tiết: ví dụ mốc thời gian sai thứ tự

| loi | order_id | mua | duyet | ban_giao | giao |
| --- | --- | --- | --- | --- | --- |
| bàn giao trước duyệt | 000576fe… | 2018-07-04 12:08:27 | 2018-07-05 16:35:48 | 2018-07-05 12:15:00 | 2018-07-09 14:04:07 |
| bàn giao trước duyệt | 00217570… | 2018-04-22 12:13:25 | 2018-04-24 17:24:48 | 2018-04-23 19:03:19 | 2018-05-02 20:38:44 |
| giao trước bàn giao | 0922ee16… | 2017-07-11 10:45:44 | 2017-07-11 10:55:15 | 2017-07-14 12:41:34 | 2017-07-12 20:49:42 |
| giao trước bàn giao | 19feb562… | 2016-10-07 17:09:56 | 2016-10-07 17:32:09 | 2016-10-26 11:42:05 | 2016-10-20 19:07:54 |
| delivered thiếu ngày giao | 0d3268ba… | 2018-07-01 21:14:02 | 2018-07-01 21:29:54 | 2018-07-03 09:28:00 | nan |
| delivered thiếu ngày giao | 20edc82c… | 2018-06-27 16:09:12 | 2018-06-27 16:29:30 | 2018-07-03 19:26:00 | nan |

## Chi tiết: cơ cấu loại thanh toán

| Loại | Số lần | % |
| --- | ---: | ---: |
| credit_card | 76.795 | 73,92% |
| boleto | 19.784 | 19,04% |
| voucher | 5.775 | 5,56% |
| debit_card | 1.529 | 1,47% |
| not_defined | 3 | 0,00% |
