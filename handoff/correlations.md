# Tương quan và các mối quan hệ chính (olist_full)

*Sinh tự động bởi `scripts/eda/correlations.py` trên database `olist_full`; chạy lại script để cập nhật số liệu.*

Tập dữ liệu: 96.470 đơn đã giao (status = delivered, có ngày giao khách). Các khoảng thời gian âm (lỗi nguồn) được đặt NULL trước khi tính. Dùng hệ số **Spearman** (theo thứ hạng) vì hầu hết biến lệch phải mạnh.

## Ma trận tương quan

Hình: `figures/3-3-1_correlation_matrix.png`.

| Cặp biến | Spearman ρ |
| --- | ---: |
| Tiền hàng (price) – Tổng thanh toán | 0,99 |
| Ngày vận chuyển – Lead time (mua → giao) | 0,89 |
| Phí vận chuyển – Tổng thanh toán | 0,57 |
| Tổng cân nặng (g) – Tổng thanh toán | 0,56 |
| Tiền hàng (price) – Tổng cân nặng (g) | 0,54 |
| Phí vận chuyển – Tổng cân nặng (g) | 0,49 |
| Tiền hàng (price) – Phí vận chuyển | 0,47 |
| Phí vận chuyển – Ngày vận chuyển | 0,41 |

Tương quan của điểm review với các biến khác (mạnh nhất trước): Lead time (mua → giao) -0,23; Ngày vận chuyển -0,20; Trễ so với dự kiến (ngày) -0,18; Số dòng hàng -0,11.

## Trễ giao hàng và điểm review

Hình: `figures/3-3-1_delay_vs_review.png`.

| Nhóm | Số đơn có review | Điểm TB | % review tiêu cực (≤ 2) | % review 5 sao |
| --- | ---: | ---: | ---: | ---: |
| Sớm (< 0 ngày) | 88.163 | 4,29 | 9,2% | 62,4% |
| Đúng hạn (0 ngày) | 1.280 | 4,04 | 12,3% | 50,5% |
| Trễ 1–3 ngày | 1.852 | 3,29 | 32,2% | 33,2% |
| Trễ 4–7 ngày | 1.748 | 2,11 | 67,6% | 14,1% |
| Trễ > 7 ngày | 2.781 | 1,70 | 79,2% | 7,0% |

- Spearman giữa delay_days và điểm review: ρ = -0,18.
- Đơn giao đúng/sớm có điểm TB 4,29, còn đơn trễ > 7 ngày chỉ 1,70 (chênh 2,60 điểm); tỷ lệ review tiêu cực tăng từ 9,2% (giao sớm) lên 79,2% (trễ > 7 ngày).

## Phí vận chuyển và cân nặng

Hình: `figures/3-3-1_freight_vs_weight.png`.

- 112.241 dòng hàng có cân nặng và phí > 0: Spearman ρ = 0,45. Phí tăng theo cân nặng nhưng độ phân tán lớn (phí còn phụ thuộc quãng đường và kích thước), nên không thể thay thế bằng công thức theo cân nặng.

## Lead time theo vùng

Hình: `figures/3-3-1_lead_time_by_region.png`.

| Vùng | Số đơn đã giao | Trung bình (ngày) | Trung vị (ngày) | P95 (ngày) |
| --- | ---: | ---: | ---: | ---: |
| Sudeste | 66.193 | 10,8 | 8,7 | 25,3 |
| Sul | 13.813 | 14,0 | 12,1 | 29,7 |
| Centro-Oeste | 5.624 | 15,0 | 13,3 | 29,0 |
| Nordeste | 9.044 | 20,0 | 17,3 | 40,5 |
| Norte | 1.796 | 22,6 | 20,2 | 43,5 |

- Vùng nhanh nhất: Sudeste (trung vị 8,7 ngày); chậm nhất: Norte (trung vị 20,2 ngày).

## Tỷ lệ giao trễ theo bang

Hình: `figures/3-3-1_late_rate_by_state.png`.

- Tỷ lệ giao trễ toàn quốc: 6,8% số đơn đã giao.
- Bang trễ nhiều nhất: AL 21,4% (n = 397), MA 17,4% (n = 717), SE 15,2% (n = 335), PI 13,9% (n = 476), CE 13,8% (n = 1.279).
- Bang trễ ít nhất: AP 3,0% (n = 67), RO 2,9% (n = 243), AM 2,8% (n = 145).
- Lưu ý: các bang có rất ít đơn (n nhỏ) thì tỷ lệ kém ổn định.

| Bang | Vùng | Số đơn đã giao | % trễ |
| --- | --- | ---: | ---: |
| AL | Nordeste | 397 | 21,4% |
| MA | Nordeste | 717 | 17,4% |
| SE | Nordeste | 335 | 15,2% |
| PI | Nordeste | 476 | 13,9% |
| CE | Nordeste | 1.279 | 13,8% |
| RR | Norte | 41 | 12,2% |
| BA | Nordeste | 3.256 | 12,2% |
| RJ | Sudeste | 12.350 | 12,1% |
| PA | Norte | 946 | 11,2% |
| ES | Sudeste | 1.995 | 10,7% |
| PB | Nordeste | 517 | 10,4% |
| TO | Norte | 274 | 9,9% |
| MS | Centro-Oeste | 701 | 9,7% |
| PE | Nordeste | 1.593 | 9,6% |
| RN | Nordeste | 474 | 9,3% |
| SC | Sul | 3.546 | 8,2% |
| GO | Centro-Oeste | 1.957 | 6,5% |
| RS | Sul | 5.344 | 6,1% |
| MT | Centro-Oeste | 886 | 6,0% |
| DF | Centro-Oeste | 2.080 | 5,7% |
| MG | Sudeste | 11.354 | 4,6% |
| SP | Sudeste | 40.494 | 4,5% |
| PR | Sul | 4.923 | 4,0% |
| AC | Norte | 80 | 3,8% |
| AP | Norte | 67 | 3,0% |
| RO | Norte | 243 | 2,9% |
| AM | Norte | 145 | 2,8% |
