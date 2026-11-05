-- setup: required
-- 6 fact tables (DW_DESIGN section 7). PK = grain, every FK NOT NULL (-1 = Unknown member) with a B-tree index.
-- Money numeric(12,2); durations numeric(10,2); flags are 0/1 integers so they can be summed.

CREATE TABLE IF NOT EXISTS dw.fact_order_item (          -- transaction
    order_id char(32) NOT NULL, order_item_id int NOT NULL,
    purchase_date_key int NOT NULL REFERENCES dw.dim_date (date_key),
    shipping_limit_date_key int NOT NULL REFERENCES dw.dim_date (date_key),
    customer_key int NOT NULL REFERENCES dw.dim_customer (customer_key),
    customer_geography_key int NOT NULL REFERENCES dw.dim_geography (geography_key),
    seller_geography_key int NOT NULL REFERENCES dw.dim_geography (geography_key),
    seller_key int NOT NULL REFERENCES dw.dim_seller (seller_key),
    product_key int NOT NULL REFERENCES dw.dim_product (product_key),
    order_status_key int NOT NULL REFERENCES dw.dim_order_status (order_status_key),
    price numeric(12,2) NOT NULL, freight_value numeric(12,2) NOT NULL, item_total numeric(12,2) NOT NULL,
    etl_batch_id bigint NOT NULL,
    PRIMARY KEY (order_id, order_item_id));

CREATE TABLE IF NOT EXISTS dw.fact_order_fulfillment (   -- accumulating snapshot
    order_id char(32) PRIMARY KEY,
    customer_key int NOT NULL REFERENCES dw.dim_customer (customer_key),
    customer_geography_key int NOT NULL REFERENCES dw.dim_geography (geography_key),
    order_status_key int NOT NULL REFERENCES dw.dim_order_status (order_status_key),
    purchase_date_key int NOT NULL REFERENCES dw.dim_date (date_key),
    approved_date_key int NOT NULL REFERENCES dw.dim_date (date_key),
    carrier_date_key int NOT NULL REFERENCES dw.dim_date (date_key),
    delivered_date_key int NOT NULL REFERENCES dw.dim_date (date_key),
    estimated_date_key int NOT NULL REFERENCES dw.dim_date (date_key),
    purchase_ts timestamp, approved_ts timestamp, carrier_ts timestamp, delivered_ts timestamp, estimated_ts timestamp,
    approval_hours numeric(10,2), handling_days numeric(10,2), transit_days numeric(10,2), lead_days numeric(10,2),
    delay_days int, promised_days int,
    is_delivered int NOT NULL, is_late int NOT NULL, is_canceled int NOT NULL,
    item_count int NOT NULL, seller_count int NOT NULL,
    order_value numeric(12,2) NOT NULL, freight_total numeric(12,2) NOT NULL, payment_total numeric(12,2) NOT NULL,
    dq_flag_count int NOT NULL, etl_batch_id bigint NOT NULL);

CREATE TABLE IF NOT EXISTS dw.fact_payment (             -- transaction
    order_id char(32) NOT NULL, payment_sequential int NOT NULL,
    purchase_date_key int NOT NULL REFERENCES dw.dim_date (date_key),
    customer_key int NOT NULL REFERENCES dw.dim_customer (customer_key),
    payment_type_key int NOT NULL REFERENCES dw.dim_payment_type (payment_type_key),
    payment_installments int NOT NULL, payment_value numeric(12,2) NOT NULL,
    etl_batch_id bigint NOT NULL,
    PRIMARY KEY (order_id, payment_sequential));

CREATE TABLE IF NOT EXISTS dw.fact_review (              -- transaction
    review_id char(32) NOT NULL, order_id char(32) NOT NULL,
    review_creation_date_key int NOT NULL REFERENCES dw.dim_date (date_key),
    review_answer_date_key int NOT NULL REFERENCES dw.dim_date (date_key),
    customer_key int NOT NULL REFERENCES dw.dim_customer (customer_key),
    review_score int NOT NULL CHECK (review_score BETWEEN 1 AND 5),
    is_negative int NOT NULL, has_comment_title int NOT NULL, has_comment_message int NOT NULL,
    comment_length int NOT NULL, response_hours numeric(10,2), delivered_late int NOT NULL,
    etl_batch_id bigint NOT NULL,
    PRIMARY KEY (review_id, order_id));

CREATE TABLE IF NOT EXISTS dw.fact_lead_funnel (         -- accumulating snapshot
    mql_id char(32) PRIMARY KEY, landing_page_id char(32),
    first_contact_date_key int NOT NULL REFERENCES dw.dim_date (date_key),
    won_date_key int NOT NULL REFERENCES dw.dim_date (date_key),
    first_sale_date_key int NOT NULL REFERENCES dw.dim_date (date_key),
    lead_origin_key int NOT NULL REFERENCES dw.dim_lead_origin (lead_origin_key),
    lead_profile_key int NOT NULL REFERENCES dw.dim_lead_profile (lead_profile_key),
    seller_key int NOT NULL REFERENCES dw.dim_seller (seller_key),
    sdr_key int NOT NULL REFERENCES dw.dim_sales_rep (sales_rep_key),
    sr_key int NOT NULL REFERENCES dw.dim_sales_rep (sales_rep_key),
    is_won int NOT NULL, has_first_sale int NOT NULL,
    days_to_close int, days_won_to_first_sale int,
    declared_product_catalog_size numeric(12,1), declared_monthly_revenue numeric(14,2),
    seller_gmv_first_90d numeric(12,2),
    etl_batch_id bigint NOT NULL);

CREATE TABLE IF NOT EXISTS dw.fact_seller_monthly (      -- periodic snapshot, dense
    month_date_key int NOT NULL REFERENCES dw.dim_date (date_key),
    seller_key int NOT NULL REFERENCES dw.dim_seller (seller_key),
    orders int NOT NULL, items int NOT NULL, gmv numeric(12,2) NOT NULL, freight numeric(12,2) NOT NULL,
    delivered_orders int NOT NULL, late_orders int NOT NULL, late_rate numeric(7,4), canceled_orders int NOT NULL,
    avg_review_score numeric(4,2), is_active int NOT NULL, months_since_first_sale int NOT NULL,
    etl_batch_id bigint NOT NULL,
    PRIMARY KEY (month_date_key, seller_key));

-- B-tree index on every foreign key column that is not already the leading column of the primary key
CREATE INDEX IF NOT EXISTS ix_foi_purchase_date ON dw.fact_order_item (purchase_date_key);
CREATE INDEX IF NOT EXISTS ix_foi_ship_limit_date ON dw.fact_order_item (shipping_limit_date_key);
CREATE INDEX IF NOT EXISTS ix_foi_customer ON dw.fact_order_item (customer_key);
CREATE INDEX IF NOT EXISTS ix_foi_customer_geo ON dw.fact_order_item (customer_geography_key);
CREATE INDEX IF NOT EXISTS ix_foi_seller_geo ON dw.fact_order_item (seller_geography_key);
CREATE INDEX IF NOT EXISTS ix_foi_seller ON dw.fact_order_item (seller_key);
CREATE INDEX IF NOT EXISTS ix_foi_product ON dw.fact_order_item (product_key);
CREATE INDEX IF NOT EXISTS ix_foi_status ON dw.fact_order_item (order_status_key);
CREATE INDEX IF NOT EXISTS ix_foi_batch ON dw.fact_order_item (etl_batch_id);

CREATE INDEX IF NOT EXISTS ix_fof_customer ON dw.fact_order_fulfillment (customer_key);
CREATE INDEX IF NOT EXISTS ix_fof_customer_geo ON dw.fact_order_fulfillment (customer_geography_key);
CREATE INDEX IF NOT EXISTS ix_fof_status ON dw.fact_order_fulfillment (order_status_key);
CREATE INDEX IF NOT EXISTS ix_fof_purchase_date ON dw.fact_order_fulfillment (purchase_date_key);
CREATE INDEX IF NOT EXISTS ix_fof_approved_date ON dw.fact_order_fulfillment (approved_date_key);
CREATE INDEX IF NOT EXISTS ix_fof_carrier_date ON dw.fact_order_fulfillment (carrier_date_key);
CREATE INDEX IF NOT EXISTS ix_fof_delivered_date ON dw.fact_order_fulfillment (delivered_date_key);
CREATE INDEX IF NOT EXISTS ix_fof_estimated_date ON dw.fact_order_fulfillment (estimated_date_key);

CREATE INDEX IF NOT EXISTS ix_fp_purchase_date ON dw.fact_payment (purchase_date_key);
CREATE INDEX IF NOT EXISTS ix_fp_customer ON dw.fact_payment (customer_key);
CREATE INDEX IF NOT EXISTS ix_fp_payment_type ON dw.fact_payment (payment_type_key);

CREATE INDEX IF NOT EXISTS ix_fr_order ON dw.fact_review (order_id);
CREATE INDEX IF NOT EXISTS ix_fr_creation_date ON dw.fact_review (review_creation_date_key);
CREATE INDEX IF NOT EXISTS ix_fr_answer_date ON dw.fact_review (review_answer_date_key);
CREATE INDEX IF NOT EXISTS ix_fr_customer ON dw.fact_review (customer_key);

CREATE INDEX IF NOT EXISTS ix_flf_first_contact_date ON dw.fact_lead_funnel (first_contact_date_key);
CREATE INDEX IF NOT EXISTS ix_flf_won_date ON dw.fact_lead_funnel (won_date_key);
CREATE INDEX IF NOT EXISTS ix_flf_first_sale_date ON dw.fact_lead_funnel (first_sale_date_key);
CREATE INDEX IF NOT EXISTS ix_flf_origin ON dw.fact_lead_funnel (lead_origin_key);
CREATE INDEX IF NOT EXISTS ix_flf_profile ON dw.fact_lead_funnel (lead_profile_key);
CREATE INDEX IF NOT EXISTS ix_flf_seller ON dw.fact_lead_funnel (seller_key);
CREATE INDEX IF NOT EXISTS ix_flf_sdr ON dw.fact_lead_funnel (sdr_key);
CREATE INDEX IF NOT EXISTS ix_flf_sr ON dw.fact_lead_funnel (sr_key);

CREATE INDEX IF NOT EXISTS ix_fsm_seller ON dw.fact_seller_monthly (seller_key);

-- ---------------------------------------------------------------- metadata (Vietnamese comments)
DO $$
DECLARE
    r record;
BEGIN
    FOR r IN SELECT * FROM (VALUES
        ('fact_order_item', NULL, 'Fact giao dịch: 1 dòng / sản phẩm trong 1 đơn (order_id, order_item_id). Dùng cho GMV, doanh thu theo danh mục / seller / vùng'),
        ('fact_order_item', 'order_id', 'Mã đơn (degenerate dimension)'), ('fact_order_item', 'order_item_id', 'Số thứ tự dòng trong đơn (degenerate dimension)'),
        ('fact_order_item', 'purchase_date_key', 'Ngày mua -> dim_date'), ('fact_order_item', 'shipping_limit_date_key', 'Hạn seller bàn giao cho vận chuyển -> dim_date'),
        ('fact_order_item', 'customer_key', 'Phiên bản SCD2 của khách có hiệu lực tại ngày mua -> dim_customer'),
        ('fact_order_item', 'customer_geography_key', 'Địa lý khách (vai trò 1) -> dim_geography'), ('fact_order_item', 'seller_geography_key', 'Địa lý seller (vai trò 2) -> dim_geography'),
        ('fact_order_item', 'seller_key', '-> dim_seller'), ('fact_order_item', 'product_key', '-> dim_product'), ('fact_order_item', 'order_status_key', 'Trạng thái đơn -> dim_order_status'),
        ('fact_order_item', 'price', 'Giá bán (BRL), additive'), ('fact_order_item', 'freight_value', 'Phí vận chuyển phân bổ cho dòng (BRL), additive'),
        ('fact_order_item', 'item_total', 'price + freight_value'), ('fact_order_item', 'etl_batch_id', 'Lô ETL đã nạp dòng này'),
        ('fact_order_fulfillment', NULL, 'Fact accumulating snapshot: 1 dòng / đơn hàng, cập nhật (UPSERT) khi đơn đi qua mốc mới; dùng cho thời gian xử lý, giao trễ, hủy'),
        ('fact_order_fulfillment', 'order_id', 'Mã đơn (khoá chính, degenerate dimension)'), ('fact_order_fulfillment', 'customer_key', 'Phiên bản SCD2 của khách tại ngày mua'),
        ('fact_order_fulfillment', 'customer_geography_key', 'Địa lý khách -> dim_geography'), ('fact_order_fulfillment', 'order_status_key', '-> dim_order_status'),
        ('fact_order_fulfillment', 'purchase_date_key', 'Mốc 1: ngày mua'), ('fact_order_fulfillment', 'approved_date_key', 'Mốc 2: ngày duyệt thanh toán (-1 nếu chưa xảy ra)'),
        ('fact_order_fulfillment', 'carrier_date_key', 'Mốc 3: ngày bàn giao cho vận chuyển (-1 nếu chưa)'), ('fact_order_fulfillment', 'delivered_date_key', 'Mốc 4: ngày giao khách (-1 nếu chưa)'),
        ('fact_order_fulfillment', 'estimated_date_key', 'Mốc 5: ngày giao dự kiến'),
        ('fact_order_fulfillment', 'purchase_ts', 'Thời điểm mua (gốc)'), ('fact_order_fulfillment', 'approved_ts', 'Thời điểm duyệt (gốc)'),
        ('fact_order_fulfillment', 'carrier_ts', 'Thời điểm bàn giao vận chuyển (gốc)'), ('fact_order_fulfillment', 'delivered_ts', 'Thời điểm giao khách (gốc)'),
        ('fact_order_fulfillment', 'estimated_ts', 'Thời điểm giao dự kiến (gốc)'),
        ('fact_order_fulfillment', 'approval_hours', 'Giờ từ mua đến duyệt; NULL nếu thiếu mốc hoặc âm (lỗi nguồn)'),
        ('fact_order_fulfillment', 'handling_days', 'Ngày từ duyệt đến bàn giao vận chuyển; NULL nếu thiếu mốc hoặc âm'),
        ('fact_order_fulfillment', 'transit_days', 'Ngày từ bàn giao đến giao khách; NULL nếu thiếu mốc hoặc âm'),
        ('fact_order_fulfillment', 'lead_days', 'Ngày từ mua đến giao khách; NULL nếu thiếu mốc hoặc âm'),
        ('fact_order_fulfillment', 'delay_days', 'Ngày giao thực tế - ngày dự kiến (theo ngày; âm = giao sớm)'),
        ('fact_order_fulfillment', 'promised_days', 'Ngày dự kiến - ngày mua = số ngày Olist hứa giao; NULL nếu âm'),
        ('fact_order_fulfillment', 'is_delivered', '1 nếu trạng thái delivered và có ngày giao'), ('fact_order_fulfillment', 'is_late', '1 nếu đã giao và delay_days > 0'),
        ('fact_order_fulfillment', 'is_canceled', '1 nếu trạng thái canceled'), ('fact_order_fulfillment', 'item_count', 'Số dòng sản phẩm của đơn'),
        ('fact_order_fulfillment', 'seller_count', 'Số seller khác nhau trong đơn'), ('fact_order_fulfillment', 'order_value', 'Σ price của đơn'),
        ('fact_order_fulfillment', 'freight_total', 'Σ freight_value của đơn'), ('fact_order_fulfillment', 'payment_total', 'Σ payment_value của đơn'),
        ('fact_order_fulfillment', 'dq_flag_count', 'Số cờ lỗi dữ liệu của đơn ở ODS + số khoảng thời gian bị đặt NULL vì âm'),
        ('fact_order_fulfillment', 'etl_batch_id', 'Lô ETL cuối cùng ghi dòng này'),
        ('fact_payment', NULL, 'Fact giao dịch: 1 lần thanh toán (order_id, payment_sequential)'),
        ('fact_payment', 'order_id', 'Mã đơn'), ('fact_payment', 'payment_sequential', 'Lần thanh toán thứ mấy của đơn'),
        ('fact_payment', 'purchase_date_key', 'Ngày mua của đơn -> dim_date'), ('fact_payment', 'customer_key', '-> dim_customer'),
        ('fact_payment', 'payment_type_key', '-> dim_payment_type'), ('fact_payment', 'payment_installments', 'Số kỳ trả góp (>= 1)'),
        ('fact_payment', 'payment_value', 'Giá trị thanh toán (BRL)'), ('fact_payment', 'etl_batch_id', 'Lô ETL đã nạp'),
        ('fact_review', NULL, 'Fact giao dịch: 1 review gắn với 1 đơn (review_id, order_id)'),
        ('fact_review', 'review_id', 'Mã review'), ('fact_review', 'order_id', 'Mã đơn'),
        ('fact_review', 'review_creation_date_key', 'Ngày tạo review -> dim_date'), ('fact_review', 'review_answer_date_key', 'Ngày trả lời review -> dim_date (-1 nếu không có)'),
        ('fact_review', 'customer_key', '-> dim_customer'), ('fact_review', 'review_score', 'Điểm 1-5'), ('fact_review', 'is_negative', '1 nếu điểm <= 2'),
        ('fact_review', 'has_comment_title', '1 nếu có tiêu đề'), ('fact_review', 'has_comment_message', '1 nếu có nội dung'),
        ('fact_review', 'comment_length', 'Số ký tự nội dung (0 nếu không có)'), ('fact_review', 'response_hours', 'Giờ từ tạo đến trả lời; NULL nếu thiếu hoặc âm'),
        ('fact_review', 'delivered_late', '1 nếu đơn được giao trễ (lấy từ fact_order_fulfillment)'), ('fact_review', 'etl_batch_id', 'Lô ETL đã nạp'),
        ('fact_lead_funnel', NULL, 'Fact accumulating snapshot: 1 dòng / MQL; cập nhật khi MQL được chốt (won) và khi seller có đơn đầu'),
        ('fact_lead_funnel', 'mql_id', 'Mã MQL (khoá chính)'), ('fact_lead_funnel', 'landing_page_id', 'Trang đích (degenerate)'),
        ('fact_lead_funnel', 'first_contact_date_key', 'Mốc 1: ngày liên hệ đầu'), ('fact_lead_funnel', 'won_date_key', 'Mốc 2: ngày chốt deal (-1 nếu chưa chốt)'),
        ('fact_lead_funnel', 'first_sale_date_key', 'Mốc 3: ngày mua của đơn đầu tiên của seller (-1 nếu chưa)'),
        ('fact_lead_funnel', 'lead_origin_key', '-> dim_lead_origin'), ('fact_lead_funnel', 'lead_profile_key', '-> dim_lead_profile (-1 nếu chưa chốt)'),
        ('fact_lead_funnel', 'seller_key', '-> dim_seller (-1 nếu chưa chốt)'), ('fact_lead_funnel', 'sdr_key', 'Nhân viên SDR -> dim_sales_rep'), ('fact_lead_funnel', 'sr_key', 'Nhân viên SR -> dim_sales_rep'),
        ('fact_lead_funnel', 'is_won', '1 nếu đã chốt deal'), ('fact_lead_funnel', 'has_first_sale', '1 nếu seller đã có đơn'),
        ('fact_lead_funnel', 'days_to_close', 'Ngày từ liên hệ đầu đến chốt; NULL nếu chưa chốt hoặc âm (lỗi nguồn)'),
        ('fact_lead_funnel', 'days_won_to_first_sale', 'Ngày từ chốt đến đơn đầu; NULL nếu chưa có hoặc âm (seller bán trước khi chốt)'),
        ('fact_lead_funnel', 'declared_product_catalog_size', 'Số sản phẩm khai báo (non-additive, dùng AVG/median)'),
        ('fact_lead_funnel', 'declared_monthly_revenue', 'Doanh thu tháng khai báo (non-additive)'),
        ('fact_lead_funnel', 'seller_gmv_first_90d', 'GMV (đơn không bị Failed) của seller trong 90 ngày kể từ ngày đơn đầu tiên; NULL nếu chưa có đơn'),
        ('fact_lead_funnel', 'etl_batch_id', 'Lô ETL cuối cùng ghi dòng này'),
        ('fact_seller_monthly', NULL, 'Fact periodic snapshot: 1 seller x 1 tháng, dày đặc từ tháng có đơn đầu đến tháng cuối có đơn trong dữ liệu'),
        ('fact_seller_monthly', 'month_date_key', 'Ngày 1 của tháng -> dim_date'), ('fact_seller_monthly', 'seller_key', '-> dim_seller'),
        ('fact_seller_monthly', 'orders', 'Số đơn (distinct) có seller này trong tháng, mọi trạng thái'), ('fact_seller_monthly', 'items', 'Số dòng sản phẩm'),
        ('fact_seller_monthly', 'gmv', 'Σ price của đơn không bị Failed (khớp định nghĩa GMV)'), ('fact_seller_monthly', 'freight', 'Σ freight_value của đơn không bị Failed'),
        ('fact_seller_monthly', 'delivered_orders', 'Số đơn đã giao'), ('fact_seller_monthly', 'late_orders', 'Số đơn giao trễ'),
        ('fact_seller_monthly', 'late_rate', 'late_orders / delivered_orders; NULL nếu chưa có đơn giao'), ('fact_seller_monthly', 'canceled_orders', 'Số đơn bị hủy'),
        ('fact_seller_monthly', 'avg_review_score', 'Điểm review trung bình; NULL nếu không có review'), ('fact_seller_monthly', 'is_active', '1 nếu orders > 0'),
        ('fact_seller_monthly', 'months_since_first_sale', 'Số tháng kể từ tháng có đơn đầu của seller (0 = tháng đầu)'), ('fact_seller_monthly', 'etl_batch_id', 'Lô ETL đã ghi')
    ) AS t(tbl, col, cmt)
    LOOP
        IF r.col IS NULL THEN
            EXECUTE format('COMMENT ON TABLE dw.%I IS %L', r.tbl, r.cmt);
        ELSE
            EXECUTE format('COMMENT ON COLUMN dw.%I.%I IS %L', r.tbl, r.col, r.cmt);
        END IF;
    END LOOP;
END $$;
