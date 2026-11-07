# 05 – Nghiệp vụ (BẢN NHÁP để nhóm sửa và vẽ lại)

> **Đây là bản nháp.** Quy trình dựa trên các cột thời gian của dữ liệu Olist (mỗi mốc là một cột) và mô tả công khai về Olist; **không phải tài liệu chính thức của doanh nghiệp**. Nhóm cần đọc, sửa cho đúng cách hiểu của mình, rồi vẽ lại bằng draw.io / Visio (đúng ký hiệu BPMN) cho báo cáo mục 3.1 và 3.2.1–3.2.2.
> Hình PNG được render tự động từ các khối Mermaid trong file này bằng `python scripts/render_mermaid.py` (sửa khối Mermaid rồi chạy lại để có hình mới). Ký hiệu: **hình thoi vàng "📊" = điểm kho dữ liệu thu thập** (cột/bảng ghi lại sự kiện để phân tích).

## 1. Quy trình xử lý đơn hàng (BPMN nháp)
Các mốc có dữ liệu: `order_purchase_timestamp` → `order_approved_at` → `order_delivered_carrier_date` → `order_delivered_customer_date`; `order_estimated_delivery_date` được tính lúc đặt hàng; review sau khi giao. Trạng thái đơn: created, approved, invoiced, processing, shipped, delivered, canceled, unavailable.

<!-- png: 3-2-1_bpmn_don_hang.png -->
```mermaid
flowchart LR
    subgraph KH["Khách hàng"]
        A(["Bắt đầu: chọn hàng trên sàn"]) --> B["Đặt hàng và thanh toán"]
        Z["Nhận hàng, đánh giá 1-5 sao"] --> END1(["Kết thúc"])
    end
    subgraph OL["Olist / sàn"]
        C{"Thanh toán hợp lệ?"}
        D["Duyệt thanh toán"]
        X["Hủy đơn"]
    end
    subgraph SE["Seller"]
        E["Chuẩn bị và đóng gói hàng"]
        F["Bàn giao cho đơn vị vận chuyển"]
    end
    subgraph VC["Vận chuyển"]
        G["Vận chuyển đến khách"]
        H["Giao hàng"]
    end
    B --> C
    C -- "Có" --> D --> E --> F --> G --> H --> Z
    C -- "Không / hết hàng" --> X --> END1
    K1{{"📊 purchase_ts, ngày dự kiến: fact_order_fulfillment"}} -.-> B
    K2{{"📊 approval_hours = duyệt - mua"}} -.-> D
    K3{{"📊 handling_days = bàn giao - duyệt; shipping_limit_date"}} -.-> F
    K4{{"📊 transit_days; lead_days; delay_days; is_late"}} -.-> H
    K5{{"📊 fact_review: review_score, is_negative, response_hours"}} -.-> Z
    K6{{"📊 is_canceled, status_group = Failed"}} -.-> X
    K7{{"📊 fact_payment: loại, số kỳ, giá trị"}} -.-> B
    classDef kho fill:#FFF3C4,stroke:#E0A100,color:#000
    class K1,K2,K3,K4,K5,K6,K7 kho
```

| Bước | Mốc dữ liệu (cột) | Nơi kho lưu | Phân tích được |
| --- | --- | --- | --- |
| Đặt hàng, thanh toán | `order_purchase_timestamp`, `payment_type`, `payment_installments` | `fact_order_fulfillment.purchase_ts`, `fact_payment` | số đơn, cơ cấu thanh toán, trả góp |
| Duyệt | `order_approved_at` | `approval_hours` | tốc độ duyệt (TB 10,3 giờ) |
| Bàn giao vận chuyển | `order_delivered_carrier_date`, `shipping_limit_date` | `handling_days` | seller xử lý chậm hay nhanh (TB 2,9 ngày) |
| Giao khách | `order_delivered_customer_date` | `transit_days`, `lead_days`, `delay_days`, `is_late` | vận chuyển (TB 9,3 ngày), đúng hạn 93,2% |
| Đánh giá | `review_score`, `review_creation_date`, `review_answer_timestamp` | `fact_review` | điểm TB 4,09; ảnh hưởng của trễ |
| Hủy / không khả dụng | `order_status` | `is_canceled`, `dim_order_status` | tỷ lệ Failed 1,24% |

## 2. Quy trình thu hút seller (BPMN nháp)
Dữ liệu CRM có hai mốc: `first_contact_date` (MQL liên hệ đầu) và `won_date` (chốt deal); mốc thứ ba (đơn đầu tiên) lấy từ hệ thống bán hàng nhờ nối `seller_id`.

<!-- png: 3-2-2_bpmn_thu_hut_seller.png -->
```mermaid
flowchart LR
    subgraph MK["Marketing"]
        A(["Bắt đầu: doanh nghiệp nhỏ biết đến Olist"]) --> B["Vào landing page và để lại thông tin (origin: organic, paid, social, email...)"]
    end
    subgraph SD["Đội sales"]
        C["SDR liên hệ và đánh giá MQL"]
        D{"Đủ điều kiện?"}
        E["SR tư vấn và chốt deal"]
        F{"Chốt được?"}
    end
    subgraph SL["Seller"]
        G["Ký hợp đồng, tạo tài khoản seller"]
        H["Đăng sản phẩm, nhận đơn đầu tiên"]
        I(["Seller hoạt động: có đơn hằng tháng"])
    end
    B --> C --> D
    D -- "Có" --> E --> F
    D -- "Không" --> LOST1(["Loại"])
    F -- "Có" --> G --> H --> I
    F -- "Không" --> LOST2(["Mất lead"])
    K1{{"📊 fact_lead_funnel: first_contact_date_key, lead_origin_key, landing_page_id"}} -.-> B
    K2{{"📊 dim_sales_rep: SDR; days_to_close = chốt - liên hệ"}} -.-> C
    K3{{"📊 won_date_key, is_won, dim_lead_profile (business_segment, lead_type...)"}} -.-> E
    K4{{"📊 dim_seller: is_from_funnel, acquisition_channel, won_date"}} -.-> G
    K5{{"📊 first_sale_date_key, days_won_to_first_sale, seller_gmv_first_90d"}} -.-> H
    K6{{"📊 fact_seller_monthly: orders, gmv, late_rate, avg_review_score"}} -.-> I
    classDef kho fill:#FFF3C4,stroke:#E0A100,color:#000
    class K1,K2,K3,K4,K5,K6 kho
```

Số liệu: 8.000 MQL → 842 chốt (10,5%, TB 48,5 ngày) → 379 seller có đơn bán được (45,0% số đã chốt; TB 51,9 ngày từ chốt đến đơn đầu).

## 3. Business Model Canvas của Olist (9 ô, bản nháp)
*Suy luận từ dữ liệu và mô tả công khai về Olist (sàn kết nối người bán nhỏ với các marketplace lớn ở Brazil); các ô về doanh thu và đối tác cần nhóm kiểm tra lại.*

| Ô | Nội dung |
| --- | --- |
| **1. Phân khúc khách hàng** | **Người bán**: doanh nghiệp / hộ kinh doanh nhỏ (reseller, manufacturer; các `business_segment` như đồ gia dụng, điện thoại, sức khoẻ-làm đẹp…). **Người mua cuối** tại Brazil (96.096 khách, 65% GMV ở vùng Sudeste). |
| **2. Giá trị đề xuất** | Seller nhỏ bán được trên nhiều marketplace qua **một hợp đồng và một hệ thống** (đơn, hậu cần, thanh toán); người mua mua ở sàn quen thuộc với vận chuyển thống nhất. |
| **3. Kênh** | Kênh thu hút seller: `organic_search`, `paid_search`, `social`, `email`, `referral`, `direct_traffic`, `display`… (landing page); kênh bán: các marketplace đối tác. |
| **4. Quan hệ khách hàng** | Với seller: đội sales (SDR tìm, SR chốt), onboarding, hỗ trợ; với người mua: đánh giá sau giao, dịch vụ hậu mãi. |
| **5. Dòng doanh thu** | *(suy luận, cần xác nhận)* phí/hoa hồng trên đơn bán qua nền tảng và phí dịch vụ cho seller. Dữ liệu cho biết giá hàng và phí vận chuyển (GMV 13,49 triệu BRL; phí vận chuyển ≈ 16,6% giá hàng), không có doanh thu của Olist. |
| **6. Nguồn lực chính** | Nền tảng công nghệ tích hợp marketplace, dữ liệu đơn hàng và đánh giá, đội marketing và sales, hợp đồng logistics. |
| **7. Hoạt động chính** | Thu hút và chốt seller; tích hợp sản phẩm; xử lý đơn (duyệt, theo dõi bàn giao, vận chuyển); thanh toán; chăm sóc sau giao và thu thập đánh giá. |
| **8. Đối tác chính** | Các marketplace lớn; đơn vị vận chuyển / logistics; đơn vị thanh toán (thẻ, boleto, voucher); seller. |
| **9. Cơ cấu chi phí** | Công nghệ và vận hành nền tảng; hậu cần và vận chuyển; marketing (paid search, display) và đội sales; xử lý thanh toán; chăm sóc khách. |

![Business Model Canvas](../figures/3-2-3_business_model_canvas.png)

## 4. Cây nghiệp vụ (các hoạt động của doanh nghiệp)
<!-- png: 3-2-5_cay_nghiep_vu.png -->
```mermaid
mindmap
  root((Olist))
    Thu hút seller
      Marketing: landing page, kênh organic, paid, social, email
      Sales: SDR tìm lead, SR chốt deal
      Onboarding: ký hợp đồng, tạo tài khoản, đăng sản phẩm
    Quản lý đơn hàng
      Nhận đơn và thanh toán
      Duyệt đơn
      Bàn giao vận chuyển
      Vận chuyển và giao hàng
      Hủy và không khả dụng
    Chăm sóc khách
      Thu thập đánh giá
      Phản hồi review
    Quản lý seller
      Theo dõi doanh số
      Theo dõi giao trễ và đánh giá
    Quản trị dữ liệu và phân tích
      Kho dữ liệu
      Báo cáo và dashboard
```

## 5. Cây yêu cầu phân tích
<!-- png: 3-2-6_cay_yeu_cau_phan_tich.png -->
```mermaid
mindmap
  root((Yêu cầu phân tích))
    Bán hàng
      GMV, đơn, AOV theo thời gian
      Danh mục và nhóm ngành hàng
      Vùng và bang, phí vận chuyển
      Tăng trưởng MoM, YoY và quy luật 80/20
    Xử lý đơn
      Thời gian từng chặng
      Tỷ lệ giao trễ và hủy
      Ngày hứa giao so với thực tế
      Vùng nào chậm
    Thanh toán
      Cơ cấu hình thức thanh toán
      Số kỳ trả góp
    Trải nghiệm khách
      Điểm review và % tiêu cực
      Giao trễ ảnh hưởng điểm thế nào
      Khách quay lại, RFM, cohort
    Seller
      Seller GMV cao nhưng hay trễ
      Scorecard seller
    Thu hút seller
      Chuyển đổi MQL sang seller theo kênh
      Thời gian chốt deal
      Thời gian đến đơn đầu
      GMV seller theo kênh
```

## 6. Cây phân tích của từng dashboard
Mỗi cây: mục tiêu → câu hỏi → chỉ số (measure) → chiều. Chi tiết từng dashboard ở `huong-dan/dashboards/D1.md … D7.md`.

<!-- png: 3-2-7_cay_phan_tich_D1.png -->
```mermaid
mindmap
  root((D1 Executive Overview))
    Câu hỏi
      Doanh thu bao nhiêu và đang tăng hay giảm
      Giao hàng có đúng hạn không
      Khách hài lòng không
    Chỉ số
      GMV, Orders, AOV
      GMV MoM %, YoY %
      On-time rate, Cancel rate
      Avg review
    Chiều
      Tháng
      Vùng
      Nhóm ngành hàng
```

<!-- png: 3-2-7_cay_phan_tich_D2.png -->
```mermaid
mindmap
  root((D2 Sales và Product))
    Câu hỏi
      Ngành hàng nào bán chạy
      Danh mục nào tạo 80 phần trăm GMV
      Phí vận chuyển nặng ở đâu
    Chỉ số
      GMV, Items, AOV
      Freight ratio
      Cum share Pareto
    Chiều
      Nhóm ngành, danh mục, sản phẩm
      Quý, tháng
      Bang, cỡ hàng
```

<!-- png: 3-2-7_cay_phan_tich_D3.png -->
```mermaid
mindmap
  root((D3 Order Fulfillment))
    Câu hỏi
      Đơn mất bao lâu ở từng chặng
      Vùng nào giao trễ
      Lời hứa giao có sát thực tế không
    Chỉ số
      Avg approval hours, handling days, transit days
      On-time rate, Late rate
      Promised vs actual
      Cancel rate
    Chiều
      Tháng
      Bang, vùng
      Nhóm trễ
      Trạng thái đơn
```

<!-- png: 3-2-7_cay_phan_tich_D4.png -->
```mermaid
mindmap
  root((D4 Geography và Freight))
    Câu hỏi
      GMV tập trung ở đâu
      Phí vận chuyển tăng theo khoảng cách thế nào
      Seller và khách có cùng bang không
    Chỉ số
      GMV, Freight, Freight ratio
      GMV by seller state
      Avg lead days
      Khoảng cách km
    Chiều
      Vùng, bang, thành phố, zip
      Nhóm ngành, cỡ hàng
      Nhóm khoảng cách
```

<!-- png: 3-2-7_cay_phan_tich_D5.png -->
```mermaid
mindmap
  root((D5 Customer Experience))
    Câu hỏi
      Giao trễ ảnh hưởng điểm review ra sao
      Khách thanh toán bằng gì
      Khách có quay lại không
    Chỉ số
      Avg review, percent negative
      Payment share, Avg installments
      Repeat customer rate
      RFM, retention
    Chiều
      Nhóm trễ
      Hình thức thanh toán
      Phân khúc RFM
      Cohort
```

<!-- png: 3-2-7_cay_phan_tich_D6.png -->
```mermaid
mindmap
  root((D6 Seller Acquisition))
    Câu hỏi
      Kênh nào chuyển đổi MQL tốt
      Chốt deal mất bao lâu
      Seller từ funnel bán thế nào
    Chỉ số
      MQLs, Won deals, MQL to won rate
      Avg days to close
      Won to first sale rate
      Seller GMV first 90d
      Small sample warning
    Chiều
      Origin, nhóm kênh
      Phân khúc kinh doanh
      Seller, bang
```

<!-- png: 3-2-7_cay_phan_tich_D7.png -->
```mermaid
mindmap
  root((D7 Data Quality và ETL))
    Câu hỏi
      Pipeline chạy có ổn không
      Bao nhiêu dòng bị loại và vì sao
      Test có đạt không
    Chỉ số
      Duration sec, rows inserted
      Pass percent
      Row count rejected
      Funnel lấp đầy dần
    Chiều
      Lô ETL
      Chế độ full hoặc incremental
      Lý do loại
```

## 7. Việc cho nhóm
- Đọc kỹ mục 1–2 và **sửa cho khớp cách nhóm hiểu nghiệp vụ**; vẽ lại BPMN chuẩn trong draw.io (có thể dùng thư viện hình BPMN sẵn có), giữ nguyên các **điểm thu thập dữ liệu** (📊).
- Kiểm tra mục 3 (Business Model Canvas): ô doanh thu và đối tác cần nguồn công khai để dẫn chứng; chỉnh lại câu chữ.
- Dùng mục 4–6 làm cơ sở cho mục báo cáo 3.2.1–3.2.2 và 3.3.5; ghép hình `3-2-*.png`.
