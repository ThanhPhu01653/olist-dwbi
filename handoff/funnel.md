# Marketing funnel (olist_full)

*Sinh tự động bởi `scripts/eda/funnel.py` trên database `olist_full`; chạy lại script để cập nhật số liệu.*

GMV của seller = tổng `price` của các đơn không bị hủy/không khả dụng (DW_DESIGN §9).

## MQL theo tháng và kênh

Hình: `figures/3-3-1_funnel_mql_by_month.png`.

- 8.000 MQL, liên hệ đầu từ 2017-06 đến 2018-05; tháng nhiều nhất 2018-04 (1.352 MQL).
- Số MQL theo kênh (cao → thấp): organic_search 2.296, paid_search 1.586, social 1.350, unknown 1.159, direct_traffic 499, email 493, referral 284, other 150, display 118, other_publicities 65.

## Tỷ lệ chốt deal theo kênh

Hình: `figures/3-3-1_funnel_win_rate_by_origin.png`.

| origin | MQL | Đã chốt | Tỷ lệ chốt |
| --- | ---: | ---: | ---: |
| unknown | 1.159 | 193 | 16,7% |
| paid_search | 1.586 | 195 | 12,3% |
| organic_search | 2.296 | 271 | 11,8% |
| direct_traffic | 499 | 56 | 11,2% |
| referral | 284 | 24 | 8,5% |
| social | 1.350 | 75 | 5,6% |
| display | 118 | 6 | 5,1% |
| other_publicities | 65 | 3 | 4,6% |
| email | 493 | 15 | 3,0% |
| other | 150 | 4 | 2,7% |

- Tỷ lệ chốt chung 10,5% (842 / 8.000). Kênh cao nhất: unknown (16,7%); thấp nhất: other (2,7%).

## Thời gian chốt deal

Hình: `figures/3-3-1_funnel_days_to_close.png`.

- 841 deal hợp lệ (loại deal có ngày chốt trước ngày liên hệ đầu): trung vị 14 ngày, trung bình 48,5 ngày, P90 162 ngày, dài nhất 427 ngày.

## Phân khúc kinh doanh (business_segment)

Hình: `figures/3-3-1_funnel_business_segment.png`.

| business_segment | Số deal | % |
| --- | ---: | ---: |
| home_decor | 105 | 12,5% |
| health_beauty | 93 | 11,0% |
| car_accessories | 77 | 9,1% |
| household_utilities | 71 | 8,4% |
| construction_tools_house_garden | 69 | 8,2% |
| audio_video_electronics | 64 | 7,6% |
| computers | 34 | 4,0% |
| pet | 30 | 3,6% |
| food_supplement | 28 | 3,3% |
| food_drink | 26 | 3,1% |

## Seller trong closed_deals có / không có đơn hàng

Hình: `figures/3-3-1_funnel_seller_overlap.png`.

| Nhóm | Số seller | % |
| --- | ---: | ---: |
| Có đơn hàng trong order_items | 380 | 45,1% |
| Có trong oltp.sellers nhưng chưa có đơn | 0 | 0,0% |
| Không có trong oltp.sellers | 462 | 54,9% |
| Tổng deal | 842 | 100,0% |

- **380 / 842 seller từ funnel (45,1%) có đơn hàng**; 462 seller (54,9%) không có trong hệ thống bán hàng.
- Nhóm có đơn: 4.518 đơn, **tổng GMV 674.005,39 BRL** (0,67 triệu), chiếm 4,99% GMV toàn sàn (13,49 triệu BRL); trung bình 1.774 BRL / seller.
- Các seller còn lại có đơn (2.715 seller, không nằm trong deal đã chốt có đơn) trung bình 4.722 BRL / seller.
- Từ ngày chốt đến đơn đầu tiên (nhóm có đơn): trung vị 44 ngày; không có seller nào có đơn đầu trước ngày chốt (won_date), nên `days_won_to_first_sale` luôn không âm.
- Mọi seller trong `oltp.sellers` đều có ít nhất một đơn (3.095 seller, 3.095 seller có dòng hàng): bảng sellers của hệ thống bán hàng chỉ chứa seller đã bán được.
