# Phân phối dữ liệu (olist_full)

*Sinh tự động bởi `scripts/eda/distributions.py` trên database `olist_full`; chạy lại script để cập nhật số liệu.*

GMV = tổng `price` của các đơn không bị hủy/không khả dụng (đúng định nghĩa KPI ở DW_DESIGN §9).

## Biến số chính

Hình: `figures/3-3-1_distributions_numeric.png`.

| Biến | Số quan sát | Trung bình | Trung vị | P95 | P99 | Min | Max | Giá trị = 0 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Giá sản phẩm (price) | 112.650 | 120,65 | 74,99 | 349,90 | 890,00 | 0,85 | 6.735 | 0 |
| Phí vận chuyển (freight_value) | 112.650 | 19,99 | 16,26 | 45,12 | 84,52 | 0,00 | 409,68 | 383 |
| Giá trị thanh toán (payment_value) | 103.886 | 154,10 | 100,00 | 437,63 | 1.040 | 0,00 | 13.664 | 9 |
| Lead time: mua → giao (lead_days) | 96.470 | 12,56 | 10,22 | 29,27 | 46,05 | 0,53 | 209,63 | 0 |
| Chênh lệch so với dự kiến (delay_days) | 96.470 | -11,88 | -12,00 | 3,00 | 18,00 | -147,00 | 188,00 | 0 |

- Giá sản phẩm lệch phải rất mạnh: trung bình 120,65 BRL nhưng trung vị chỉ 74,99 BRL; 1% dòng hàng đắt nhất có giá từ 890 BRL, cao nhất 6.735 BRL.
- Lead time (mua → giao) của 96.470 đơn đã giao: trung vị 10,2 ngày, P95 29,3 ngày, tối đa 210 ngày.
- delay_days: 91,9% đơn giao sớm hơn ngày dự kiến, 1,3% đúng ngày, 6,8% giao trễ (trung vị -12 ngày, tức thường giao sớm hơn dự kiến).

## Pareto theo danh mục

Hình: `figures/3-3-1_pareto_category.png`.

- 18 / 74 danh mục (24,3%) tạo ra 80% GMV; tổng GMV 13,49 triệu BRL.
- 5 danh mục đứng đầu chiếm 39,8% GMV; danh mục số 1 (`health_beauty`) chiếm 9,3%.

| Hạng | Danh mục (tiếng Anh) | GMV (triệu BRL) | Số đơn |
| ---: | --- | ---: | ---: |
| 1 | health_beauty | 1,26 | 8.800 |
| 2 | watches_gifts | 1,20 | 5.604 |
| 3 | bed_bath_table | 1,04 | 9.399 |
| 4 | sports_leisure | 0,98 | 7.673 |
| 5 | computers_accessories | 0,90 | 6.654 |
| 6 | furniture_decor | 0,73 | 6.425 |
| 7 | housewares | 0,63 | 5.847 |
| 8 | cool_stuff | 0,62 | 3.616 |
| 9 | auto | 0,59 | 3.872 |
| 10 | garden_tools | 0,48 | 3.505 |

## Pareto theo seller

Hình: `figures/3-3-1_pareto_seller.png`.

- 540 / 3.053 seller có đơn hợp lệ (17,7%) tạo ra 80% GMV (trong tổng 3.095 seller của hệ thống).
- 5 seller đứng đầu chiếm 7,7% GMV; seller số 1 chiếm 1,7%.

## Số đơn theo tháng

Hình: `figures/3-3-1_orders_per_month.png`.

- Giai đoạn 2017-01 → 2018-08 có 99.092 đơn (99,6% tổng số đơn).
- Ngoài giai đoạn đó: 2016 chỉ 329 đơn (tháng có đơn: 2016-09, 2016-10, 2016-12); 2018-09 và 2018-10 chỉ 20 đơn (2018-09: 16, 2018-10: 4).
- Tháng cao nhất: 2017-11 với 7.544 đơn.

| Tháng | Số đơn |
| --- | ---: |
| 2016-09 | 4 |
| 2016-10 | 324 |
| 2016-11 | 0 |
| 2016-12 | 1 |
| 2017-01 | 800 |
| 2017-02 | 1.780 |
| 2017-03 | 2.682 |
| 2017-04 | 2.404 |
| 2017-05 | 3.700 |
| 2017-06 | 3.245 |
| 2017-07 | 4.026 |
| 2017-08 | 4.331 |
| 2017-09 | 4.285 |
| 2017-10 | 4.631 |
| 2017-11 | 7.544 |
| 2017-12 | 5.673 |
| 2018-01 | 7.269 |
| 2018-02 | 6.728 |
| 2018-03 | 7.211 |
| 2018-04 | 6.939 |
| 2018-05 | 6.873 |
| 2018-06 | 6.167 |
| 2018-07 | 6.292 |
| 2018-08 | 6.512 |
| 2018-09 | 16 |
| 2018-10 | 4 |

## Phân bố điểm đánh giá

Hình: `figures/3-3-1_review_score.png`.

| Điểm | Số review | % |
| --- | ---: | ---: |
| 1 | 11.424 | 11,5% |
| 2 | 3.151 | 3,2% |
| 3 | 8.179 | 8,2% |
| 4 | 19.142 | 19,3% |
| 5 | 57.328 | 57,8% |

- Điểm trung bình 4,09; 77,1% review từ 4 sao trở lên; 14,7% review tiêu cực (≤ 2 sao).
