# P12c – Tương quan: nói rõ dùng hệ số nào, vì sao; thêm kiểm định cho biến phân loại

Chạy **sau khi P12b đã merge**. Làm trên nhánh `phase/P12c`, xong thì merge vào `main` và push. Không sửa `huong-dan/` (nhóm đang dùng bản PDF cũ). Chỉ sửa `02a-kham-pha.tex`, `99-du-phong.tex`, `scripts/eda/`, và nếu cần, `report/chapters/3-1-kham-pha.tex`.

## Bối cảnh

Khi nghe nhóm 6 và nhóm 10 trình bày, thầy hỏi về heatmap tương quan: dùng hệ số gì, vì sao. Sau đó thầy gửi tài liệu về phân tích quan hệ giữa các biến **không phải số**:
- kiểm định Chi-Square về tính độc lập (p-value);
- Cramér's V (độ mạnh, đối xứng);
- Theil's U (có hướng, bất đối xứng);
- MCA (nhiều biến, bản đồ 2D);
- hồi quy logistic đa thức (Odds Ratio).

Tài liệu nằm ở `attach/Phan-tich-tuong-quan-bien-phan-loai.docx`. Chỉ đọc để biết phương pháp; không chép câu chữ, không chép ví dụ.

Phần tương quan của nhóm đã đúng hướng:
- Spearman cho biến số;
- tỉ số tương quan η cho cặp biến phân loại – biến số;
- Cramér's V (hiệu chỉnh Bergsma) cho cặp biến phân loại.

Nhưng **trên slide chưa nói vì sao chọn**, và còn thiếu bốn chỗ thầy sẽ hỏi:
1. Chưa có p-value của kiểm định χ². Với n khoảng 100.000 đơn, gần như cặp nào cũng có p < 0,05, nên phải đọc độ mạnh (V) chứ không đọc p. Câu này phải nói được.
2. Chưa có Theil's U, tức chưa đo được chiều: biết A thì đoán B tốt hơn bao nhiêu, và ngược lại.
3. Ma trận Spearman (`3-3-1_correlation_matrix.png`) chỉ có trong báo cáo. Ma trận này có các cặp tương quan **do định nghĩa**, không phải phát hiện:
   - tiền hàng – tổng thanh toán 0,99 (thanh toán = tiền hàng + phí);
   - ngày vận chuyển – lead time 0,89 (thành phần của nhau).

   Nếu chiếu ma trận này mà không đánh dấu thì sẽ bị hỏi đúng kiểu thầy hỏi nhóm 6 (r = 1,00 giữa dư nợ và giá trị tài sản).
4. Chưa có bước nhiều biến (MCA, hồi quy logistic). Không bắt buộc, nhưng có một slide dự phòng thì trả lời được khi bị hỏi.

## 1. Tính toán (`scripts/eda/p8_association.py` hoặc script mới `p12c_categorical.py`)

Dùng cùng dữ liệu và cùng 7 biến phân loại như hiện tại.

**a. Kiểm định χ²** cho 21 cặp: χ², bậc tự do, p-value, số ô kỳ vọng < 5. Ô kỳ vọng < 5 quá 20% thì dùng Monte Carlo hoặc gộp nhóm, và ghi rõ đã làm gì.

**b. Theil's U** (hệ số bất định) cho 21 cặp, cả hai chiều:

$$U(X \mid Y) = \frac{H(X) - H(X \mid Y)}{H(X)}$$

Vẽ heatmap **không đối xứng**: hàng = biến cần đoán, cột = biến đã biết. Lưu vào `figures/3-1_theils_u_heatmap.png`, cùng kiểu và cùng bảng màu với hình Cramér's V, chữ đủ to để chiếu.

**c. Ma trận Spearman cho slide** (`figures/3-1_spearman_slide.png`):
- giữ tối đa 8 biến chính;
- bỏ biến trùng định nghĩa (chỉ giữ một trong tiền hàng / tổng thanh toán);
- nếu phải giữ cặp thành phần (lead time và ngày vận chuyển) thì đánh dấu ô bằng ký hiệu và ghi chú dưới hình "tương quan do định nghĩa";
- chỉ giữ nửa dưới tam giác.

**d. Odds Ratio cho cặp mạnh nhất (cờ trễ → review tiêu cực):**
- bảng 2×2: tỷ lệ review tiêu cực ở đơn trễ so với đơn đúng hạn, kèm OR và khoảng tin cậy 95%;
- thêm hồi quy logistic: review tiêu cực (1–2 sao) theo cờ trễ, có kiểm soát vùng khách và nhóm ngành, để thấy OR của cờ trễ còn lớn khi đã tính vùng.

  Nếu khác biệt giữa OR thô và OR có kiểm soát lớn thì ghi lại. Nếu muốn dùng multinomial (3 nhóm review) thì được, nhưng slide chỉ đưa một con số OR dễ hiểu.

**e. MCA (cho slide dự phòng):**
- trên 4 biến: cờ trễ, nhóm review, vùng khách, trạng thái đơn;
- dùng `prince`, hoặc tự tính bằng SVD trên ma trận chỉ báo nếu không cài được;
- vẽ bản đồ 2 chiều các nhóm (`figures/3-1_mca.png`), ghi % quán tính của 2 trục;
- nếu 2 trục giải thích quá ít thì vẫn vẽ nhưng ghi rõ, không kết luận quá.

Ghi mọi con số vào `handoff/2026-11-25-P12c-tuong-quan.md` và một bảng `.tex` cho báo cáo (`report/tables/p12c_*.tex`).

## 2. Slide (`02a-kham-pha.tex`, khối Tương quan)

Giữ quy tắc của P12b: chỉ nói cái lớn, không thêm quá **2 frame** vào bộ chính.

**Frame mới (đầu khối Tương quan): "Tương quan: chọn phương pháp theo loại biến".** Bảng `BangTC` 3 dòng:

| Cặp biến | Phương pháp | Vì sao | Kết quả nổi bật của nhóm |
| --- | --- | --- | --- |
| số – số | Spearman | biến lệch phải (skewness 4–7), nhiều ngoại lai; Pearson chỉ đo quan hệ tuyến tính | khoảng cách – phí 0,63 |
| phân loại – số | tỉ số tương quan η | đo phần phương sai của biến số do nhóm giải thích | review theo cờ trễ η = 0,392 |
| phân loại – phân loại | χ² → Cramér's V → Theil's U | χ²: có liên hệ không; V: mạnh đến đâu; U: theo chiều nào | cờ trễ – nhóm review V = 0,40 |

Thêm `\KetLuan` (một câu): với n khoảng 100.000, p gần như luôn < 0,05 nên nhóm đọc độ mạnh, không đọc p. Kiểm tra lại các con số trong bảng bằng kết quả tính ở mục 1 và handoff P8. Số nào khác thì dùng số mới tính và ghi lại.

**Frame Cramér's V hiện có:** đổi thành hai lớp bấm:
- `\only<1>`: Cramér's V, mỗi ô có dấu * nếu p < 0,05, ghi chú dưới hình;
- `\only<2>`: Theil's U.

`\KetLuan` nói chiều của cặp mạnh nhất, ví dụ "Biết đơn trễ giảm X% độ bất định về nhóm review; chiều ngược lại chỉ Y%".

**Fact–fact:** frame khoảng cách / phí / lead time giữ nguyên. Ma trận Spearman mới để ở `99-du-phong.tex` cùng ghi chú "tương quan do định nghĩa". Nếu P12b còn chỗ trong bộ chính thì có thể đưa vào thay một slide thưa, không bắt buộc.

**Odds Ratio:** đưa vào frame "Tương quan dim–fact: giao trễ và điểm review" một dòng hoặc một thẻ số, kiểu "Đơn trễ: odds review tiêu cực gấp X lần (đã kiểm soát vùng và ngành)". Không thêm frame.

**`99-du-phong.tex`:** thêm 2–3 frame (MCA, bảng χ² đầy đủ, ma trận Spearman), mỗi frame có `\KetLuan`.

**`\note` của frame "chọn phương pháp"** cho người nói: 4–5 câu trả lời ngắn cho các câu thầy có thể hỏi:
- vì sao không dùng Pearson;
- vì sao không đọc p-value;
- V khác U thế nào;
- tương quan không phải nhân quả;
- vì sao bỏ cặp tiền hàng – thanh toán.

## 3. Báo cáo (nếu `report/chapters/3-1-kham-pha.tex` đã có mục tương quan)

- Bổ sung đoạn kiểm định χ² và Theil's U.
- Thay hình ma trận Spearman cũ bằng bản đã đánh dấu tương quan do định nghĩa, hoặc thêm chú thích.
- Thêm bảng `p12c_*.tex`.
- Chỉ bổ sung, không viết lại cả chương.

## 4. Kiểm tra
1. Chạy lại script từ đầu, số liệu ra giống nhau. Ghi lệnh chạy vào handoff.
2. Chạy `latexmk -lualatex main.tex` (slide và báo cáo): không lỗi.
3. Chạy `python scripts/kiem_tra_slide.py --strict slides/sections/02a-kham-pha.tex slides/sections/99-du-phong.tex`: 0 LỖI.
4. Chạy `--anh` cho các trang đã sửa. Mở từng ảnh, kiểm heatmap đọc được ở 1280 px.
5. Tạo lại `slides_overleaf.zip`, `report_overleaf.zip`, `slides/main.pdf`.

## Kết thúc
- Commit đúng file, merge, push.

Báo lại cho Phú:
- bảng kết quả χ², V, U của 5 cặp mạnh nhất;
- OR thô và OR có kiểm soát;
- MCA giải thích bao nhiêu %;
- danh sách frame đã sửa hoặc thêm (bộ chính và dự phòng);
- ảnh xem trước các trang đó;
- đoạn trả lời câu hỏi trong `\note`, để Phú gửi người trình bày phần khám phá dữ liệu.
