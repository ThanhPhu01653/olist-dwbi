# P12c – Tương quan: chọn phương pháp, kiểm định χ², Theil's U, odds ratio, MCA – 2026-11-25

## Đã làm

- Script `scripts/eda/p12c_categorical.py` (database `olist_full`, hạt giống ngẫu nhiên cố định nên số giống nhau mỗi lần chạy). Chạy: `python scripts/eda/p12c_categorical.py` (PowerShell và bash giống nhau).
- Dùng cùng dữ liệu và cùng bảy biến phân loại của P8 (hình thức thanh toán, nhóm ngành, vùng khách, vùng seller, trạng thái đơn, cờ giao trễ, nhóm review), 21 cặp.
- **Kiểm định χ²:** 19/21 cặp có p < 0,05. Với n khoảng 100.000, p gần như luôn nhỏ nên p không phân biệt được cặp mạnh với cặp yếu; phải đọc độ mạnh (V) chứ không đọc p.
- **Ô kỳ vọng < 5:** 6 cặp có hơn 20% ô kỳ vọng nhỏ hơn 5, p của các cặp này tính bằng Monte Carlo (2000 lần hoán vị, p nhỏ nhất có thể là 1/2001 ≈ 0,0005); cột "cách tính p" ghi rõ.
- **Theil's U:** U(X | Y) = (H(X) − H(X | Y)) / H(X), entropy tự nhiên; hàng là biến cần đoán, cột là biến đã biết (không đối xứng).

## Số liệu

### Năm cặp mạnh nhất (xếp theo V hiệu chỉnh) và ba cặp tiếp theo

| Cặp biến | n | χ² | bậc tự do | p | ô kỳ vọng < 5 | V | U (hàng | cột) | U (cột | hàng) |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Cờ giao trễ – Nhóm review | 95.830 | 15.562 | 2 | < 0,001 | 0% | 0,403 | 0,222 | 0,083 |
| Trạng thái đơn – Nhóm review | 98.673 | 9.649 | 14 | < 0,001 | 25% | 0,221 | 0,187 | 0,047 |
| Nhóm ngành hàng – Vùng seller | 98.666 | 4.997 | 48 | < 0,001 | 18% | 0,112 | 0,011 | 0,043 |
| Vùng khách – Cờ giao trễ | 96.476 | 577 | 4 | < 0,001 | 0% | 0,077 | 0,003 | 0,010 |
| Vùng khách – Vùng seller | 98.666 | 2.086 | 16 | < 0,001 | 16% | 0,072 | 0,009 | 0,016 |
| Hình thức thanh toán – Trạng thái đơn | 99.440 | 940 | 28 | < 0,001 | 48% | 0,048 | 0,002 | 0,007 |
| Nhóm ngành hàng – Vùng khách | 98.666 | 865 | 48 | < 0,001 | 0% | 0,046 | 0,002 | 0,005 |
| Nhóm ngành hàng – Nhóm review | 97.917 | 285 | 24 | < 0,001 | 0% | 0,036 | 0,001 | 0,002 |

`U (hàng | cột)`: biến đầu của cặp là biến cần đoán, biến sau là biến đã biết; cột còn lại là chiều ngược.

### Cặp cờ giao trễ – nhóm review (cặp trung tâm)

- χ² p < 0,001; V = 0,403; η (điểm review theo cờ trễ) = 0,392.
- Biết đơn trễ thì độ bất định về nhóm review giảm **8,3%** (U(review | trễ) = 0,083); biết nhóm review thì độ bất định về cờ trễ giảm **22,2%** (U(trễ | review) = 0,222).

### Toàn bộ 21 cặp

| Cặp biến (a – b) | n | χ² | bậc tự do | p | ô < 5 | cách tính p | V | U(a|b) | U(b|a) |
| --- | ---: | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Cờ giao trễ – Nhóm review | 95.830 | 15.562 | 2 | < 0,001 | 0% | chi2 | 0,403 | 0,222 | 0,083 |
| Trạng thái đơn – Nhóm review | 98.673 | 9.649 | 14 | < 0,001 | 25% | Monte Carlo (2000) | 0,221 | 0,187 | 0,047 |
| Nhóm ngành hàng – Vùng seller | 98.666 | 4.997 | 48 | < 0,001 | 18% | chi2 | 0,112 | 0,011 | 0,043 |
| Vùng khách – Cờ giao trễ | 96.476 | 577 | 4 | < 0,001 | 0% | chi2 | 0,077 | 0,003 | 0,010 |
| Vùng khách – Vùng seller | 98.666 | 2.086 | 16 | < 0,001 | 16% | chi2 | 0,072 | 0,009 | 0,016 |
| Hình thức thanh toán – Trạng thái đơn | 99.440 | 940 | 28 | < 0,001 | 48% | Monte Carlo (2000) | 0,048 | 0,002 | 0,007 |
| Nhóm ngành hàng – Vùng khách | 98.666 | 865 | 48 | < 0,001 | 0% | chi2 | 0,046 | 0,002 | 0,005 |
| Nhóm ngành hàng – Nhóm review | 97.917 | 285 | 24 | < 0,001 | 0% | chi2 | 0,036 | 0,001 | 0,002 |
| Hình thức thanh toán – Nhóm ngành hàng | 98.665 | 415 | 36 | < 0,001 | 0% | chi2 | 0,036 | 0,003 | 0,001 |
| Vùng seller – Cờ giao trễ | 96.476 | 101 | 4 | < 0,001 | 10% | chi2 | 0,032 | 0,001 | 0,002 |
| Vùng khách – Nhóm review | 98.673 | 197 | 8 | < 0,001 | 0% | chi2 | 0,031 | 0,001 | 0,001 |
| Hình thức thanh toán – Vùng khách | 99.440 | 199 | 16 | < 0,001 | 20% | chi2 | 0,021 | 0,002 | 0,001 |
| Vùng khách – Trạng thái đơn | 99.441 | 170 | 28 | < 0,001 | 25% | Monte Carlo (2000) | 0,019 | 0,001 | 0,004 |
| Vùng seller – Nhóm review | 97.917 | 52 | 8 | < 0,001 | 13% | chi2 | 0,015 | 0,000 | 0,000 |
| Nhóm ngành hàng – Cờ giao trễ | 96.476 | 31 | 12 | 0,002 | 0% | chi2 | 0,014 | 0,000 | 0,001 |
| Hình thức thanh toán – Nhóm review | 98.672 | 45 | 8 | < 0,001 | 20% | chi2 | 0,014 | 0,000 | 0,000 |
| Hình thức thanh toán – Cờ giao trễ | 96.475 | 17 | 3 | < 0,001 | 0% | chi2 | 0,012 | 0,000 | 0,000 |
| Nhóm ngành hàng – Trạng thái đơn | 98.666 | 151 | 72 | 0,002 | 36% | Monte Carlo (2000) | 0,012 | 0,000 | 0,005 |
| Hình thức thanh toán – Vùng seller | 98.665 | 45 | 12 | < 0,001 | 10% | chi2 | 0,011 | 0,000 | 0,000 |
| Vùng seller – Trạng thái đơn | 98.666 | 40 | 24 | 0,095 | 49% | Monte Carlo (2000) | 0,006 | 0,000 | 0,001 |
| Trạng thái đơn – Cờ giao trễ | 96.476 | 1 | 1 | 0,335 | 25% | Monte Carlo (2000) | 0,000 | 0,005 | 0,000 |

### Odds ratio: giao trễ → review tiêu cực (1–2 sao)

| | Review tiêu cực | Không tiêu cực | Tỷ lệ tiêu cực |
| --- | ---: | ---: | ---: |
| Đơn trễ | 3.984 | 2.398 | 62,4% |
| Đơn đúng hạn hoặc sớm | 8.286 | 81.162 | 9,3% |

- OR thô = 16,27 (khoảng tin cậy 95%: 15,40 – 17,20), tính trên 95.830 đơn đã giao có review.
- Hồi quy logistic chỉ có cờ trễ: OR = 16,27 (trùng OR thô, đúng như dự kiến).
- Hồi quy logistic kiểm soát vùng khách và nhóm ngành (95.830 đơn): **OR = 16,28** (khoảng tin cậy 95%: 15,40 – 17,22).
- Chênh lệch OR thô và OR có kiểm soát: 16,27 → 16,28 (0,1%). Nhỏ: vùng khách và nhóm ngành hầu như không làm đổi tác động của giao trễ.
- Câu cho slide: đơn trễ có odds review tiêu cực gấp khoảng 16 lần (đã kiểm soát vùng khách và nhóm ngành).

### Ma trận Spearman cho slide

- Hai cặp do định nghĩa trong ma trận 12 biến cũ: tiền hàng – tổng thanh toán = 0,99 (thanh toán = tiền hàng + phí vận chuyển) và ngày vận chuyển – lead time = 0,89 (ngày vận chuyển là một phần của lead time). Mọi cặp có |ρ| ≥ 0,8: Tiền hàng (price) – Tổng thanh toán = 0,99; Ngày vận chuyển – Lead time (mua → giao) = 0,89.
- Hình slide giữ 8 biến (tiền hàng, phí vận chuyển, cân nặng, số kỳ trả góp, ngày vận chuyển, lead time, trễ so với dự kiến, điểm review); bỏ tổng thanh toán (trùng định nghĩa với tiền hàng), giờ chờ duyệt, ngày xử lý, số dòng hàng; chỉ nửa dưới tam giác; ô ngày vận chuyển – lead time đánh dấu † "tương quan do định nghĩa".
- Phí vận chuyển – cân nặng ρ = 0,49; trễ – điểm review ρ = -0,18; lead time – điểm review ρ = -0,23.
- Độ lệch (skewness) của các biến số: tiền hàng 9,89, phí vận chuyển 12,28, lead time 3,83 (lệch phải; cơ sở để dùng Spearman thay Pearson).

### MCA (bốn biến: giao, review, vùng khách, trạng thái đơn)

- Cách làm: phân tích tương ứng (SVD) trên ma trận chỉ báo của bốn biến (không có gói `prince`), toàn bộ 99.441 đơn. Giá trị thiếu giữ thành nhóm riêng: giao = "chưa giao", review = "chưa có review"; trạng thái đơn gộp thành ba nhóm (đã giao; hủy hoặc không khả dụng; đang xử lý hoặc vận chuyển).
- Tổng quán tính (J − Q)/Q = 2,750 với J = 15 nhóm, Q = 4 biến. Trục 1 giải thích **19,8%**, trục 2 **11,7%**, cả hai **31,5%** quán tính.
- Hiệu chỉnh Benzécri (chỉ tính trục có trị riêng > 1/Q): trục 1 94,3%, trục 2 5,6% (trong các trục được giữ).
- Quán tính thô của MCA thấp là bình thường vì ma trận chỉ báo có nhiều chiều; vì vậy chỉ đọc vị trí tương đối các nhóm, không kết luận hơn.

| Nhóm | Trục 1 | Trục 2 | Số đơn |
| --- | ---: | ---: | ---: |
| Giao: chưa giao | 5,45 | -1,48 | 2.965 |
| Giao: trễ | 0,52 | 3,23 | 6.535 |
| Giao: đúng hạn/sớm | -0,22 | -0,19 | 89.941 |
| Review: chưa có review | 1,32 | 0,41 | 768 |
| Review: tiêu cực (1-2) | 1,31 | 1,38 | 14.483 |
| Review: trung tính (3) | -0,01 | 0,29 | 8.162 |
| Review: tích cực (4-5) | -0,26 | -0,30 | 76.028 |
| Vùng: Centro-Oeste | -0,03 | 0,00 | 5.782 |
| Vùng: Nordeste | 0,17 | 0,86 | 9.394 |
| Vùng: Norte | 0,05 | 0,38 | 1.851 |
| Vùng: Sudeste | -0,00 | -0,10 | 68.266 |
| Vùng: Sul | -0,08 | -0,12 | 14.148 |
| Trạng thái: hủy/không khả dụng | 5,47 | -1,46 | 1.234 |
| Trạng thái: đang xử lý/vận chuyển | 5,45 | -1,49 | 1.729 |
| Trạng thái: đã giao | -0,17 | 0,05 | 96.478 |

## Slide và báo cáo

- `slides/sections/02a-kham-pha.tex`, khối Tương quan, bộ chính (+1 frame, không thêm frame khác): **mới** "Tương quan: chọn phương pháp theo loại biến" (bảng 3 dòng, `\note` có 5 câu trả lời); **sửa** "Tương quan dim–dim: Cramér's V 0,40, Theil's U có chiều" (hai lớp bấm: V có dấu *, Theil's U); **sửa** "Tương quan dim–fact: giao trễ và điểm review" (odds ratio 16 lần ở `\KetLuan`, số cũ chuyển vào `\note`).
- `slides/sections/99-du-phong.tex` (+3 frame): ma trận Spearman đã đánh dấu tương quan do định nghĩa; bảng χ², V, U bảy cặp mạnh nhất; bản đồ MCA.
- `report/chapters/3-1-kham-pha.tex`: thay ma trận Spearman cũ bằng bản tám biến đã đánh dấu †; thêm đoạn kiểm định χ², Theil's U, odds ratio, MCA và hai bảng `p12c_chi2.tex`, `p12c_or.tex`, hình Theil's U.
- Số trong bảng "chọn phương pháp": Spearman khoảng cách – phí 0,63 lấy từ `handoff/geo-distance.md`; η review theo cờ trễ 0,392 và V cờ trễ – review 0,403 khớp P8; skewness 3,8 đến 12,3 là số mới tính trên đơn đã giao (giá 9,89, phí 12,28, lead time 3,83), khác "4–7" ghi trong đề bài và khác số mẫu 5.000 đơn ở slide Thống kê đặc trưng.

## Câu trả lời trong `\note` của slide "chọn phương pháp" (để gửi người trình bày)

1. **Vì sao không dùng Pearson?** Giá, phí và lead time lệch phải mạnh, nhiều ngoại lai hợp lệ; Pearson chỉ đo quan hệ tuyến tính và bị vài đơn lớn kéo đi, Spearman dựa trên hạng nên bền hơn.
2. **Vì sao không đọc p-value?** Với khoảng 100.000 đơn, 19/21 cặp có p < 0,05, kể cả cặp có V chỉ 0,01; p chỉ nói có liên hệ hay không, không nói mạnh hay yếu, nên đọc V (chỉ 3 cặp có V từ 0,1).
3. **V khác U thế nào?** V đối xứng, một con số độ mạnh; U có chiều: biết nhóm review giảm 22,2% bất định về cờ trễ, biết cờ trễ giảm 8,3% bất định về nhóm review.
4. **Tương quan có phải nhân quả không?** Không: đơn trễ đi kèm review xấu (odds gấp khoảng 16 lần, đã kiểm soát vùng và ngành) nhưng nhóm không kết luận trễ gây ra điểm thấp.
5. **Vì sao bỏ cặp tiền hàng – thanh toán?** Tổng thanh toán = tiền hàng + phí vận chuyển nên ρ = 0,99 do định nghĩa; tương tự ngày vận chuyển – lead time (0,89, đánh dấu †).

## Hình / file xuất

- `figures/3-1_cramer_v_heatmap_p.png` – Cramér's V kèm dấu * cho p < 0,05.
- `figures/3-1_theils_u_heatmap.png` – Theil's U không đối xứng (hàng = biến cần đoán, cột = biến đã biết).
- `figures/3-1_spearman_slide.png` – Spearman 8 biến, nửa dưới tam giác, † cặp do định nghĩa.
- `figures/3-1_mca.png` – bản đồ MCA hai trục.
- `report/tables/p12c_chi2.tex`, `report/tables/p12c_or.tex` – bảng cho báo cáo.
