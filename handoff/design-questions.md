# Câu hỏi thiết kế cần chốt ngày 12/11 – trả lời bằng số (olist_full)

*Sinh tự động bởi `scripts/eda/design_questions.py` trên database `olist_full`; chạy lại script để cập nhật số liệu.*

Mỗi câu có số liệu, các phương án và khuyến nghị. GMV = tổng `price` của các đơn không bị hủy/không khả dụng (DW_DESIGN §9).

## Tóm tắt

| Câu | Câu hỏi | Số chính | Khuyến nghị |
| --- | --- | --- | --- |
| a | Khách có hơn 1 zip → SCD2 hay SCD1 | 250 / 96.096 khách đổi zip (0,26%); +256 phiên bản | Giữ SCD2 |
| b | Seller từ funnel có đơn / GMV → độ sâu DB4 | 380 / 842 seller có đơn; GMV 674.005 BRL (4,99% GMV sàn) | DB4 vừa phải (2 trang), gộp kênh, hiển thị cỡ mẫu |
| c | `fact_seller_monthly` dày đặc hay thưa | dày đặc 36.583 dòng, thưa 16.441 dòng | Dày đặc |
| d | Danh mục sản phẩm → bảng nhóm ngành hàng | 73 danh mục → 12 nhóm; 2 thiếu bản dịch | 12 nhóm đề xuất, nhóm duyệt các mục tranh luận |
| e | Zip thiếu trong geolocation → xây `dim_geography` | 157 zip khách + 7 zip seller thiếu; 0,28% đơn bị ảnh hưởng | Toạ độ NULL (phương án 1) |
| f | (Bổ sung) Mốc tách dữ liệu nạp ban đầu | 2017-12-31: 45.430 đơn, 2.002 MQL, 3 deal; còn 8 đợt incremental | Giữ 2017-12-31 |

## a) Bao nhiêu `customer_unique_id` có hơn 1 zip qua các đơn? (SCD2 hay SCD1 cho `dim_customer`)

**Số liệu**

| Chỉ tiêu | Giá trị |
| --- | --- |
| Số dòng customers trong nguồn (mỗi đơn một `customer_id`) | 99.441 |
| Số khách thật (`customer_unique_id`) | 96.096 |
| Khách có từ 2 đơn trở lên | 2.997 (3,1% khách) |
| Khách có hơn 1 zip trên các đơn | 250 (0,26% khách; 8,3% khách quay lại) |
|   – đúng 2 zip | 246 |
|   – đúng 3 zip | 4 |
|   – từ 4 zip trở lên (nhiều nhất 3 zip / khách) | 0 |
| Khách đổi sang bang khác | 39 |
| Số lần đổi zip (= số phiên bản SCD2 phát sinh thêm) | 256 |
| Số dòng `dim_customer` nếu SCD1 | 96.096 |
| Số dòng `dim_customer` nếu SCD2 | 96.352 (+0,27%) |
| Số đơn đặt từ một zip khác zip của đơn đầu tiên | 264 (0,27% tổng số đơn) |

**Phương án**

1. **SCD1** – ghi đè địa chỉ bằng bản mới nhất: đơn giản, mỗi khách một dòng; nhưng các đơn cũ bị gắn vào địa chỉ mới. Ảnh hưởng thực tế rất nhỏ vì địa lý của đơn đã nằm trong fact qua `customer_geography_key`, nên phân tích theo vùng không bị sai.
2. **SCD2** (đặc tả hiện tại) – giữ lịch sử địa chỉ: thêm 256 dòng (0,27%), fact phải tra khoá theo ngày mua. Chi phí thấp, đúng kỹ thuật SCD mà môn học muốn minh hoạ.
3. SCD0 (không theo dõi đổi): bỏ vì mất thông tin hiện hành.

**Khuyến nghị:** giữ **SCD2** (như DW_DESIGN §6.3). Số khách đổi zip rất ít, nên SCD2 chỉ làm dim lớn thêm 0,27% nhưng cho ví dụ SCD thật cùng dữ liệu thật để trình bày (cột `effective_from/to`, `is_current`). Lý do nên nói rõ trong báo cáo: địa lý lịch sử vẫn đúng nhờ `customer_geography_key` ở fact; SCD2 bảo đảm thuộc tính khách cũng đúng theo thời điểm.

## b) Bao nhiêu seller từ funnel có đơn hàng, và tổng GMV của họ? (độ sâu dashboard DB4)

**Số liệu**

- 842 deal đã chốt trong CRM; **380 seller (45,1%) có đơn hàng** trong hệ thống bán hàng, 462 seller (54,9%) không có đơn nào (tất cả đều không có mặt trong `oltp.sellers`).
- Nhóm có đơn: 4.518 đơn, **GMV 674.005,39 BRL** = 4,99% GMV toàn sàn (13,49 triệu BRL); trung bình 1.774 BRL / seller.
- 839 / 842 deal có ngày chốt sau 2017-12-31, tức chỉ xuất hiện qua các đợt nạp tăng dần.

| Nhóm kênh | Deal | Có đơn | % deal có đơn | GMV (BRL) | GMV TB / seller có đơn |
| --- | ---: | ---: | ---: | ---: | ---: |
| Organic | 351 | 153 | 43,6% | 246.767 | 1.613 |
| Other / Unknown | 197 | 87 | 44,2% | 221.615 | 2.547 |
| Paid | 204 | 103 | 50,5% | 153.720 | 1.492 |
| Social | 75 | 31 | 41,3% | 43.418 | 1.401 |
| Email | 15 | 6 | 40,0% | 8.485 | 1.414 |

**Phương án**

1. **DB4 đầy đủ** (funnel + hiệu suất seller + GMV theo kênh): đủ dữ liệu cho phần funnel (8.000 MQL, 842 deal) nhưng phần hiệu suất / GMV chỉ dựa trên 380 seller, và theo nhóm kênh có chỗ chỉ vài chục seller.
2. **DB4 vừa phải**: trang 1 funnel MQL → chốt → có đơn đầu tiên theo kênh và tháng; trang 2 seller từ funnel (GMV, tỷ lệ trễ, điểm review, số ngày từ chốt đến đơn đầu) với cảnh báo cỡ mẫu.
3. **DB4 chỉ funnel**: bỏ phần hiệu suất. Mất câu hỏi xuyên quy trình mà đề tài muốn trả lời.

**Khuyến nghị:** phương án 2. 45,1% deal liên kết được với đơn hàng là đủ để minh hoạ tích hợp hai nguồn qua `dim_seller`, nhưng GMV của nhóm này chỉ 4,99% GMV toàn sàn nên không nên kết luận mạnh về hiệu suất theo kênh; nên gộp kênh theo `dim_lead_origin.channel_group` (5 nhóm) và luôn hiển thị số seller. Phần 54,9% deal không có đơn nên được thể hiện rõ như một kết quả ("deal chốt nhưng chưa bán / không nằm trong sàn"), không phải lỗi dữ liệu.

## c) `fact_seller_monthly` dày đặc hay thưa: bao nhiêu dòng?

**Số liệu** (seller × tháng; “có đơn” = có ít nhất một dòng hàng trong tháng, mọi trạng thái đơn)

| Phương án | Số dòng đầy đủ | Số dòng đến 2017-12 (olist_dw ban đầu) |
| --- | ---: | ---: |
| Thưa (chỉ tháng có đơn) | 16.441 | 7.575 |
| Dày đặc: từ tháng đơn đầu của seller đến tháng cuối của dữ liệu (đặc tả hiện tại) | 36.583 | – |
| Dày đặc, cắt đến 2018-08 (giai đoạn dashboard) | 33.488 | – |
| Dày đặc, chỉ đến 2017-12 (nạp ban đầu) | 13.548 | 13.548 |

- 3.095 seller; tháng có đơn đầu tiên của kho dữ liệu 2016-09, tháng cuối 2018-09.
- Dày đặc lớn gấp 2,23 lần thưa: 44,9% số dòng dày đặc là tháng có đơn, phần còn lại (20.142 dòng) là tháng seller không bán (`is_active = 0`).

**Phương án**

1. **Thưa** (16.441 dòng): gọn, nhưng không có dòng cho tháng không bán nên khó đo seller ngưng hoạt động, `months_since_first_sale` bị đứt quãng, và biểu đồ theo tháng cần tự điền 0.
2. **Dày đặc** (36.583 dòng): đúng định nghĩa periodic snapshot của Kimball (mỗi kỳ một dòng), đo được tỷ lệ seller còn hoạt động / rời đi; tổng GMV vẫn khớp `fact_order_item`. Chi phí: 20.142 dòng thêm, vẫn rất nhỏ (dưới 37 nghìn dòng).

**Khuyến nghị:** **dày đặc** (36.583 dòng), như đặc tả; dashboard lọc giai đoạn 2017-01 → 2018-08. Dữ liệu nhỏ nên không có rủi ro hiệu năng, và dày đặc là lựa chọn mới trả lời được câu hỏi “seller nào ngưng bán”.

## d) Toàn bộ danh mục sản phẩm kèm số đơn, và bảng nhóm ngành hàng đề xuất

**Số liệu**: 73 danh mục có tên (+ nhóm `unknown` cho 610 sản phẩm rỗng danh mục) trong 32.951 sản phẩm. Số đơn và GMV tính trên đơn không bị hủy/không khả dụng (đúng định nghĩa KPI); “số đơn” là số đơn khác nhau có ít nhất một dòng hàng của danh mục.
- 2 danh mục thiếu bản dịch tiếng Anh: `portateis_cozinha_e_preparadores_de_alimentos`, `pc_gamer` → bổ sung qua `seeds/category_translation_extra.csv`.
- Mọi danh mục đều có ít nhất một đơn hợp lệ.
- Danh mục có GMV cao nhất: `beleza_saude` (9,3% GMV).

### Tổng hợp theo nhóm đề xuất (12 nhóm)

| Nhóm ngành hàng | Số danh mục | Số sản phẩm | Số dòng hàng | GMV (triệu BRL) | % GMV |
| --- | ---: | ---: | ---: | ---: | ---: |
| Home & Furniture | 16 | 9.308 | 29.775 | 3,08 | 22,8% |
| Gifts & Others | 10 | 3.122 | 12.463 | 2,10 | 15,6% |
| Electronics & Computers | 10 | 3.851 | 17.180 | 1,89 | 14,0% |
| Health & Beauty | 2 | 3.312 | 13.036 | 1,65 | 12,2% |
| Auto & Tools | 11 | 3.809 | 11.569 | 1,55 | 11,5% |
| Sports & Leisure | 1 | 2.867 | 8.590 | 0,98 | 7,3% |
| Toys & Baby | 3 | 2.342 | 7.164 | 0,89 | 6,6% |
| Office & Stationery | 2 | 1.158 | 4.195 | 0,50 | 3,7% |
| Fashion & Accessories | 8 | 1.570 | 3.721 | 0,34 | 2,5% |
| Books, Media & Music | 7 | 735 | 1.656 | 0,27 | 2,0% |
| Unknown | 1 | 610 | 1.589 | 0,18 | 1,3% |
| Food & Drinks | 3 | 267 | 1.163 | 0,07 | 0,5% |

### Chi tiết từng danh mục (xếp theo số dòng hàng giảm dần)

| Danh mục (pt) | Tiếng Anh | Nhóm đề xuất | Số sản phẩm | Số đơn | Số dòng hàng | GMV (BRL) | % GMV |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| cama_mesa_banho | bed_bath_table | Home & Furniture | 3.029 | 9.399 | 11.097 | 1.035.964 | 7,7% |
| beleza_saude | health_beauty | Health & Beauty | 2.444 | 8.800 | 9.634 | 1.255.695 | 9,3% |
| esporte_lazer | sports_leisure | Sports & Leisure | 2.867 | 7.673 | 8.590 | 979.741 | 7,3% |
| moveis_decoracao | furniture_decor | Home & Furniture | 2.657 | 6.425 | 8.298 | 727.465 | 5,4% |
| informatica_acessorios | computers_accessories | Electronics & Computers | 1.639 | 6.654 | 7.781 | 904.322 | 6,7% |
| utilidades_domesticas | housewares | Home & Furniture | 2.335 | 5.847 | 6.915 | 626.826 | 4,6% |
| relogios_presentes | watches_gifts | Gifts & Others | 1.329 | 5.604 | 5.970 | 1.198.185 | 8,9% |
| telefonia | telephony | Electronics & Computers | 1.134 | 4.183 | 4.527 | 322.343 | 2,4% |
| ferramentas_jardim | garden_tools | Auto & Tools | 753 | 3.505 | 4.328 | 481.010 | 3,6% |
| automotivo | auto | Auto & Tools | 1.900 | 3.872 | 4.204 | 586.586 | 4,3% |
| brinquedos | toys | Toys & Baby | 1.411 | 3.855 | 4.083 | 479.809 | 3,6% |
| cool_stuff | cool_stuff | Gifts & Others | 789 | 3.616 | 3.779 | 620.770 | 4,6% |
| perfumaria | perfumery | Health & Beauty | 868 | 3.146 | 3.402 | 396.599 | 2,9% |
| bebes | baby | Toys & Baby | 919 | 2.868 | 3.043 | 410.312 | 3,0% |
| eletronicos | electronics | Electronics & Computers | 517 | 2.543 | 2.755 | 157.080 | 1,2% |
| papelaria | stationery | Office & Stationery | 849 | 2.299 | 2.505 | 229.594 | 1,7% |
| fashion_bolsas_e_acessorios | fashion_bags_accessories | Fashion & Accessories | 849 | 1.858 | 2.025 | 151.623 | 1,1% |
| pet_shop | pet_shop | Gifts & Others | 719 | 1.706 | 1.942 | 213.767 | 1,6% |
| moveis_escritorio | office_furniture | Office & Stationery | 309 | 1.272 | 1.690 | 273.581 | 2,0% |
| unknown | (danh mục rỗng → unknown) | Unknown | 610 | 1.437 | 1.589 | 178.573 | 1,3% |
| consoles_games | consoles_games | Electronics & Computers | 317 | 1.054 | 1.127 | 154.927 | 1,1% |
| malas_acessorios | luggage_accessories | Fashion & Accessories | 349 | 1.030 | 1.088 | 140.111 | 1,0% |
| construcao_ferramentas_construcao | construction_tools_construction | Auto & Tools | 400 | 746 | 927 | 144.550 | 1,1% |
| eletrodomesticos | home_appliances | Home & Furniture | 370 | 762 | 769 | 80.001 | 0,6% |
| eletroportateis | small_appliances | Home & Furniture | 231 | 622 | 671 | 187.907 | 1,4% |
| instrumentos_musicais | musical_instruments | Books, Media & Music | 289 | 620 | 669 | 187.788 | 1,4% |
| casa_construcao | home_construction | Auto & Tools | 225 | 489 | 603 | 83.010 | 0,6% |
| livros_interesse_geral | books_general_interest | Books, Media & Music | 216 | 505 | 546 | 45.622 | 0,3% |
| alimentos | food | Food & Drinks | 82 | 449 | 509 | 29.244 | 0,2% |
| moveis_sala | furniture_living_room | Home & Furniture | 156 | 420 | 501 | 68.639 | 0,5% |
| casa_conforto | home_confort | Home & Furniture | 111 | 397 | 434 | 58.572 | 0,4% |
| bebidas | drinks | Food & Drinks | 81 | 296 | 378 | 22.379 | 0,2% |
| audio | audio | Electronics & Computers | 58 | 349 | 363 | 50.669 | 0,4% |
| market_place | market_place | Gifts & Others | 104 | 279 | 310 | 28.288 | 0,2% |
| construcao_ferramentas_iluminacao | construction_tools_lights | Auto & Tools | 78 | 243 | 302 | 40.002 | 0,3% |
| climatizacao | air_conditioning | Home & Furniture | 124 | 251 | 295 | 54.723 | 0,4% |
| moveis_cozinha_area_de_servico_jantar_e_jardim | kitchen_dining_laundry_garden_furniture | Home & Furniture | 94 | 246 | 279 | 46.070 | 0,3% |
| alimentos_bebidas | food_drink | Food & Drinks | 104 | 225 | 276 | 15.119 | 0,1% |
| industria_comercio_e_negocios | industry_commerce_and_business | Auto & Tools | 68 | 235 | 268 | 39.670 | 0,3% |
| livros_tecnicos | books_technical | Books, Media & Music | 123 | 260 | 267 | 19.096 | 0,1% |
| telefonia_fixa | fixed_telephony | Electronics & Computers | 116 | 214 | 261 | 57.824 | 0,4% |
| fashion_calcados | fashion_shoes | Fashion & Accessories | 173 | 238 | 260 | 23.353 | 0,2% |
| eletrodomesticos_2 | home_appliances_2 | Home & Furniture | 90 | 231 | 235 | 110.650 | 0,8% |
| construcao_ferramentas_jardim | costruction_tools_garden | Auto & Tools | 88 | 192 | 234 | 25.552 | 0,2% |
| agro_industria_e_comercio | agro_industry_and_commerce | Auto & Tools | 74 | 182 | 212 | 72.530 | 0,5% |
| artes | art | Gifts & Others | 55 | 201 | 208 | 24.168 | 0,2% |
| pcs | computers | Electronics & Computers | 30 | 181 | 203 | 222.963 | 1,7% |
| sinalizacao_e_seguranca | signaling_and_security | Auto & Tools | 93 | 140 | 199 | 21.509 | 0,2% |
| construcao_ferramentas_seguranca | construction_tools_safety | Auto & Tools | 91 | 165 | 189 | 39.589 | 0,3% |
| artigos_de_natal | christmas_supplies | Gifts & Others | 65 | 127 | 152 | 8.788 | 0,1% |
| fashion_roupa_masculina | fashion_male_clothing | Fashion & Accessories | 95 | 111 | 131 | 10.749 | 0,1% |
| fashion_underwear_e_moda_praia | fashion_underwear_beach | Fashion & Accessories | 53 | 121 | 131 | 9.542 | 0,1% |
| moveis_quarto | furniture_bedroom | Home & Furniture | 45 | 95 | 109 | 20.029 | 0,1% |
| construcao_ferramentas_ferramentas | costruction_tools_tools | Auto & Tools | 39 | 97 | 103 | 15.904 | 0,1% |
| tablets_impressao_imagem | tablets_printing_image | Electronics & Computers | 9 | 79 | 83 | 7.528 | 0,1% |
| portateis_casa_forno_e_cafe | small_appliances_home_oven_and_coffee | Home & Furniture | 31 | 75 | 76 | 47.446 | 0,4% |
| cine_foto | cine_photo | Electronics & Computers | 28 | 65 | 72 | 6.933 | 0,1% |
| dvds_blu_ray | dvds_blu_ray | Books, Media & Music | 48 | 57 | 62 | 4.559 | 0,0% |
| livros_importados | books_imported | Books, Media & Music | 31 | 53 | 60 | 4.640 | 0,0% |
| fashion_roupa_feminina | fashio_female_clothing | Fashion & Accessories | 27 | 39 | 48 | 2.804 | 0,0% |
| artigos_de_festas | party_supplies | Gifts & Others | 26 | 39 | 43 | 4.485 | 0,0% |
| fraldas_higiene | diapers_and_hygiene | Toys & Baby | 12 | 26 | 38 | 1.539 | 0,0% |
| moveis_colchao_e_estofado | furniture_mattress_and_upholstery | Home & Furniture | 10 | 38 | 38 | 4.368 | 0,0% |
| musica | music | Books, Media & Music | 27 | 38 | 38 | 6.034 | 0,0% |
| flores | flowers | Gifts & Others | 14 | 29 | 33 | 1.110 | 0,0% |
| casa_conforto_2 | home_comfort_2 | Home & Furniture | 5 | 24 | 30 | 760 | 0,0% |
| fashion_esporte | fashion_sport | Fashion & Accessories | 19 | 27 | 30 | 2.120 | 0,0% |
| artes_e_artesanato | arts_and_craftmanship | Gifts & Others | 19 | 23 | 24 | 1.814 | 0,0% |
| cds_dvds_musicais | cds_dvds_musicals | Books, Media & Music | 1 | 12 | 14 | 730 | 0,0% |
| la_cuisine | la_cuisine | Home & Furniture | 10 | 13 | 14 | 2.055 | 0,0% |
| portateis_cozinha_e_preparadores_de_alimentos | (thiếu bản dịch) | Home & Furniture | 10 | 13 | 14 | 3.934 | 0,0% |
| fashion_roupa_infanto_juvenil | fashion_childrens_clothes | Fashion & Accessories | 5 | 8 | 8 | 570 | 0,0% |
| pc_gamer | (thiếu bản dịch) | Electronics & Computers | 3 | 7 | 8 | 1.307 | 0,0% |
| seguros_e_servicos | security_and_services | Gifts & Others | 2 | 2 | 2 | 283 | 0,0% |

**Phương án**

1. Dùng 12 nhóm như bảng trên (đúng gợi ý ở DW_DESIGN §6.5, có sẵn nhóm `Unknown`).
2. Tách riêng nhóm `Pet` (từ `pet_shop`) và `Art & Crafts` (từ `artes`, `artes_e_artesanato`) để `Gifts & Others` không quá hỗn tạp. `Gifts & Others` hiện gồm 10 danh mục, 15,6% GMV.
3. Dùng thẳng danh mục gốc (73 giá trị) – không gom nhóm: quá nhiều cột cho slicer và biểu đồ.

**Khuyến nghị:** phương án 1 để chốt bản đầu; các mục dễ gây tranh luận cần nhóm duyệt: `relogios_presentes` (đồng hồ & quà tặng, GMV lớn thứ hai), `cool_stuff`, `pet_shop`, `casa_construcao` (vào Auto & Tools hay Home), `eletroportateis` / `eletrodomesticos` (vào Home hay Electronics), `fashion_esporte` (Fashion hay Sports), `instrumentos_musicais`. File nháp: `docs/category_group_draft.csv` (cột `product_category_name`, `category_group`); sau 12/11 sửa file này rồi mới nạp seed ở P2.

## e) Zip của customers / sellers không có trong geolocation

**Số liệu**

| Chỉ tiêu | Giá trị |
| --- | --- |
| Số zip khác nhau trong geolocation | 19.015 |
| Zip khác nhau của customers | 14.994 |
|   – trong đó KHÔNG có trong geolocation | 157 (1,05%) |
| Số khách (dòng customers) có zip thiếu | 278 (0,28% khách) |
| Số đơn có khách ở zip thiếu | 278 (0,28% tổng đơn) |
| GMV các đơn đó | 36.884 BRL (0,27% GMV) |
| Zip khác nhau của sellers | 2.246 |
|   – trong đó KHÔNG có trong geolocation | 7 (0,31%) |
| Số seller có zip thiếu | 7 (0,23% seller) |
| Dòng hàng của các seller đó | 253 (0,22% tổng dòng hàng) |
| GMV các dòng hàng đó | 25.857 BRL (0,19% GMV) |
| Tổng zip khác nhau nếu hợp nhất geolocation + customers + sellers (số dòng `dim_geography`) | 19.177 (thêm 162 so với geolocation) |

- Có thể điền toạ độ gần đúng bằng **trung tâm thành phố** (median toạ độ của cùng thành phố + bang trong geolocation) cho 107 / 157 zip khách và 7 / 7 zip seller thiếu.
- Có thể dùng **zip lân cận** (cùng 3 chữ số đầu) cho 156 / 157 zip khách thiếu.

**Phương án**

1. **Tạo dòng `dim_geography` từ city/state của customers / sellers, `latitude`/`longitude` = NULL** (đúng DW_DESIGN §6.2): trung thực, đơn giản; các phép tính khoảng cách seller → khách bỏ qua cặp thiếu toạ độ.
2. Như 1 nhưng **điền toạ độ gần đúng theo trung tâm thành phố** và thêm cờ `is_approx_location`: bản đồ đầy đủ hơn, nhưng thêm cột mới vào đặc tả và pha tạp dữ liệu thật với dữ liệu suy ra.
3. Loại các đơn/khách có zip thiếu: **không chấp nhận** (mất doanh thu, vi phạm nguyên tắc không bỏ dữ liệu).

**Khuyến nghị:** phương án 1. Chỉ 0,28% số đơn và 0,27% GMV bị ảnh hưởng; dim_geography vẫn đủ mọi zip (khoá ngoại luôn trỏ được), toạ độ NULL được ghi rõ trong tài liệu. Nếu nhóm cần bản đồ đầy đủ thì nâng lên phương án 2 sau, khi đó cập nhật DW_DESIGN trước.

## f) (Bổ sung) Mốc tách dữ liệu nạp ban đầu / incremental – đang chờ review ở nhật ký quyết định

**Số liệu** (tỷ lệ so với toàn bộ nguồn: 99.441 đơn, 8.000 MQL, 842 deal)

| Mốc tách | Đơn nạp ban đầu | MQL | Deal đã chốt | Số đợt incremental hằng tháng đến 2018-08 |
| --- | ---: | ---: | ---: | ---: |
| 2017-06-30 | 14.940 (15,0%) | 4 (0,1%) | 0 (0,0%) | 14 |
| 2017-12-31 | 45.430 (45,7%) | 2.002 (25,0%) | 3 (0,4%) | 8 |
| 2018-03-31 | 66.638 (67,0%) | 5.345 (66,8%) | 336 (39,9%) | 5 |
| 2018-05-31 | 80.450 (80,9%) | 8.000 (100,0%) | 665 (79,0%) | 3 |

**Phương án**

1. **2017-12-31** (đặc tả hiện tại): ranh giới năm dễ giải thích, còn 8 đợt incremental hằng tháng (2018-01 → 2018-08) để minh hoạ cập nhật; nạp ban đầu chỉ có 3 deal nên funnel được “lấp đầy dần” qua các đợt.
2. **Mốc muộn hơn** (2018-03-31 hoặc 2018-05-31): nạp ban đầu có nhiều deal hơn, nhưng còn ít đợt incremental để trình bày.
3. **Mốc sớm hơn** (2017-06-30): nhiều đợt incremental hơn nhưng nạp ban đầu quá ít dữ liệu và không có deal nào.

**Khuyến nghị:** giữ **2017-12-31**: đủ 8 đợt incremental và nạp ban đầu vẫn có hơn 45% số đơn; việc funnel gần như trống lúc đầu là điểm để kể chuyện, không phải lỗi (dashboard dựng trên trạng thái cuối).
