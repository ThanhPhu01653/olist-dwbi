# Khoảng cách seller → khách (haversine) và quan hệ với phí vận chuyển, lead time – sinh tự động

Nguồn: `mart_fulfillment.v_shipping_distance` (khoảng cách tính bằng `dw.haversine_km` trên toạ độ median của zip, không dùng PostGIS).

- Tổng dòng hàng: **112,650**. Bị bỏ khỏi phân tích vì **thiếu toạ độ** (zip của seller hoặc của khách không có toạ độ hợp lệ): **555** dòng (0.49%), thuộc 494 đơn.
- Loại thêm 549 dòng của đơn thuộc nhóm Failed; còn **111,552** dòng hàng được phân tích (109,652 dòng của đơn đã giao dùng cho lead time).
- Khoảng cách trung bình 598 km, trung vị 433 km; **36.1%** dòng hàng có seller và khách cùng bang.

## Theo nhóm khoảng cách

| Nhóm | Dòng hàng | Tỷ trọng | Freight TB (BRL) | Freight trung vị | Giá hàng TB | Freight / giá (TB) | Dòng đã giao | Lead time TB (ngày) | Lead trung vị | Tỷ lệ trễ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0-100 km | 20,787 | 18.6% | 11.75 | 9.34 | 99.76 | 24.4% | 20,465 | 6.5 | 5.1 | 4.5% |
| 100-500 km | 43,133 | 38.7% | 18.40 | 15.24 | 117.28 | 30.2% | 42,432 | 11.4 | 9.3 | 5.8% |
| 500-1000 km | 29,996 | 26.9% | 21.12 | 17.74 | 119.72 | 33.8% | 29,515 | 14.2 | 12.1 | 7.0% |
| Trên 1000 km | 17,636 | 15.8% | 31.65 | 25.38 | 153.57 | 42.8% | 17,240 | 19.0 | 16.3 | 10.3% |

## Tương quan

| Cặp biến | Pearson | Spearman | Số dòng |
| --- | ---: | ---: | ---: |
| distance_km ~ freight_value | 0.390 | 0.632 | 111,552 |
| distance_km ~ freight_ratio | 0.173 | 0.206 | 111,552 |
| distance_km ~ lead_days | 0.394 | 0.539 | 109,652 |

Pearson đo quan hệ tuyến tính, Spearman đo quan hệ đơn điệu (ít bị ảnh hưởng bởi giá trị lớn bất thường). Tương quan không chứng minh nhân quả: khoảng cách đi kèm vùng, loại hàng và cân nặng.
