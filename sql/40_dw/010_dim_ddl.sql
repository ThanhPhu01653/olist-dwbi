-- setup: required
-- 10 dimensions of the warehouse (DW_DESIGN sections 5-6). Surrogate key <name>_key (identity), natural key UNIQUE,
-- Unknown member with key -1 (inserted by dw.reset_dims() / the load procedures), technical columns dw_created_at / dw_updated_at.

CREATE TABLE IF NOT EXISTS dw.dim_date (
    date_key int PRIMARY KEY,                       -- yyyymmdd; -1 = Unknown
    full_date date UNIQUE,
    day_of_month int, day_of_week int, day_name text,
    week_of_year int, month int, month_name text, quarter int, year int,
    year_month char(7), year_quarter char(7),
    is_weekend boolean, is_holiday_br boolean, holiday_name text, is_black_friday boolean,
    dw_created_at timestamptz NOT NULL DEFAULT now(), dw_updated_at timestamptz);

CREATE TABLE IF NOT EXISTS dw.dim_geography (
    geography_key int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    zip_code_prefix char(5) UNIQUE,
    city text, state_code char(2), state_name text, region text, country text NOT NULL DEFAULT 'Brazil',
    latitude double precision, longitude double precision,
    dw_created_at timestamptz NOT NULL DEFAULT now(), dw_updated_at timestamptz);

CREATE TABLE IF NOT EXISTS dw.dim_customer (            -- SCD type 2
    customer_key int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_unique_id char(32) NOT NULL,
    zip_code_prefix char(5), city text, state_code char(2),
    geography_key int NOT NULL REFERENCES dw.dim_geography (geography_key),
    effective_from date NOT NULL, effective_to date NOT NULL,
    is_current boolean NOT NULL, version_no int NOT NULL,
    dw_created_at timestamptz NOT NULL DEFAULT now(), dw_updated_at timestamptz,
    UNIQUE (customer_unique_id, effective_from));
CREATE INDEX IF NOT EXISTS ix_dim_customer_uid ON dw.dim_customer (customer_unique_id, effective_from, effective_to);

CREATE TABLE IF NOT EXISTS dw.dim_seller (              -- SCD type 1, conformed dimension (sales + acquisition)
    seller_key int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    seller_id char(32) NOT NULL UNIQUE,
    zip_code_prefix char(5), city text, state_code char(2),
    geography_key int NOT NULL REFERENCES dw.dim_geography (geography_key),
    is_from_funnel boolean NOT NULL DEFAULT false,
    mql_id char(32), acquisition_origin text NOT NULL, acquisition_channel text NOT NULL,
    business_segment text, lead_type text, business_type text,
    won_date date, first_sale_date date,
    dw_created_at timestamptz NOT NULL DEFAULT now(), dw_updated_at timestamptz);

CREATE TABLE IF NOT EXISTS dw.dim_product (
    product_key int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id char(32) NOT NULL UNIQUE,
    category_name_pt text, category_name_en text, category_group text,
    weight_g int, length_cm int, height_cm int, width_cm int, volume_cm3 bigint, size_class text,
    photos_qty int, name_length int, description_length int,
    dw_created_at timestamptz NOT NULL DEFAULT now(), dw_updated_at timestamptz);

CREATE TABLE IF NOT EXISTS dw.dim_order_status (
    order_status_key int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_status text NOT NULL UNIQUE, status_group text NOT NULL, is_final boolean NOT NULL,
    dw_created_at timestamptz NOT NULL DEFAULT now(), dw_updated_at timestamptz);

CREATE TABLE IF NOT EXISTS dw.dim_payment_type (
    payment_type_key int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    payment_type text NOT NULL UNIQUE, payment_group text NOT NULL, display_name text NOT NULL,
    dw_created_at timestamptz NOT NULL DEFAULT now(), dw_updated_at timestamptz);

CREATE TABLE IF NOT EXISTS dw.dim_lead_origin (
    lead_origin_key int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    origin text NOT NULL UNIQUE, channel_group text NOT NULL,
    dw_created_at timestamptz NOT NULL DEFAULT now(), dw_updated_at timestamptz);

CREATE TABLE IF NOT EXISTS dw.dim_lead_profile (        -- junk dimension of the deal attributes
    lead_profile_key int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    business_segment text NOT NULL, lead_type text NOT NULL, lead_behaviour_profile text NOT NULL, business_type text NOT NULL,
    has_company text NOT NULL, has_gtin text NOT NULL, average_stock text NOT NULL,
    dw_created_at timestamptz NOT NULL DEFAULT now(), dw_updated_at timestamptz,
    UNIQUE (business_segment, lead_type, lead_behaviour_profile, business_type, has_company, has_gtin, average_stock));

CREATE TABLE IF NOT EXISTS dw.dim_sales_rep (           -- role-playing: SDR and SR
    sales_rep_key int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rep_id char(32) NOT NULL, rep_role text NOT NULL CHECK (rep_role IN ('SDR', 'SR', 'n/a')),
    dw_created_at timestamptz NOT NULL DEFAULT now(), dw_updated_at timestamptz,
    UNIQUE (rep_id, rep_role));

-- ---------------------------------------------------------------- Unknown members (key -1) and reset
CREATE OR REPLACE PROCEDURE dw.insert_unknown_members() LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO dw.dim_date (date_key, full_date, day_name, month_name, year_month, year_quarter, holiday_name)
        VALUES (-1, NULL, 'Unknown', 'Unknown', 'Unknown', 'Unknown', NULL) ON CONFLICT (date_key) DO NOTHING;
    INSERT INTO dw.dim_geography (geography_key, zip_code_prefix, city, state_code, state_name, region, country)
        OVERRIDING SYSTEM VALUE VALUES (-1, NULL, 'unknown', NULL, 'Unknown', 'Unknown', 'Brazil') ON CONFLICT (geography_key) DO NOTHING;
    INSERT INTO dw.dim_customer (customer_key, customer_unique_id, zip_code_prefix, city, state_code, geography_key, effective_from, effective_to, is_current, version_no)
        OVERRIDING SYSTEM VALUE VALUES (-1, 'unknown', NULL, 'unknown', NULL, -1, DATE '1900-01-01', DATE '9999-12-31', true, 1) ON CONFLICT (customer_key) DO NOTHING;
    INSERT INTO dw.dim_seller (seller_key, seller_id, city, geography_key, is_from_funnel, acquisition_origin, acquisition_channel)
        OVERRIDING SYSTEM VALUE VALUES (-1, 'unknown', 'unknown', -1, false, 'not_from_funnel', 'Not from funnel') ON CONFLICT (seller_key) DO NOTHING;
    INSERT INTO dw.dim_product (product_key, product_id, category_name_pt, category_name_en, category_group, size_class)
        OVERRIDING SYSTEM VALUE VALUES (-1, 'unknown', 'unknown', 'unknown', 'Unknown', 'Unknown') ON CONFLICT (product_key) DO NOTHING;
    INSERT INTO dw.dim_order_status (order_status_key, order_status, status_group, is_final)
        OVERRIDING SYSTEM VALUE VALUES (-1, 'unknown', 'Unknown', false) ON CONFLICT (order_status_key) DO NOTHING;
    INSERT INTO dw.dim_payment_type (payment_type_key, payment_type, payment_group, display_name)
        OVERRIDING SYSTEM VALUE VALUES (-1, 'unknown', 'Unknown', 'Unknown') ON CONFLICT (payment_type_key) DO NOTHING;
    INSERT INTO dw.dim_lead_origin (lead_origin_key, origin, channel_group)
        OVERRIDING SYSTEM VALUE VALUES (-1, 'n/a', 'Unknown') ON CONFLICT (lead_origin_key) DO NOTHING;
    INSERT INTO dw.dim_lead_profile (lead_profile_key, business_segment, lead_type, lead_behaviour_profile, business_type, has_company, has_gtin, average_stock)
        OVERRIDING SYSTEM VALUE VALUES (-1, 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a') ON CONFLICT (lead_profile_key) DO NOTHING;
    INSERT INTO dw.dim_sales_rep (sales_rep_key, rep_id, rep_role)
        OVERRIDING SYSTEM VALUE VALUES (-1, 'n/a', 'n/a') ON CONFLICT (sales_rep_key) DO NOTHING;
END $$;

-- full reload: empty every dimension (CASCADE also empties facts that will reference them) and recreate the Unknown members
CREATE OR REPLACE PROCEDURE dw.reset_dims() LANGUAGE plpgsql AS $$
BEGIN
    TRUNCATE dw.dim_date, dw.dim_geography, dw.dim_customer, dw.dim_seller, dw.dim_product, dw.dim_order_status, dw.dim_payment_type,
             dw.dim_lead_origin, dw.dim_lead_profile, dw.dim_sales_rep RESTART IDENTITY CASCADE;
    CALL dw.insert_unknown_members();
END $$;

CALL dw.insert_unknown_members();

-- ---------------------------------------------------------------- role-playing views of dim_date
DO $$
DECLARE
    r text;
BEGIN
    FOREACH r IN ARRAY ARRAY['purchase', 'approved', 'carrier', 'delivered', 'estimated', 'shipping_limit', 'review_creation',
                             'review_answer', 'first_contact', 'won', 'first_sale']
    LOOP
        EXECUTE format('CREATE OR REPLACE VIEW dw.v_dim_%s_date AS SELECT * FROM dw.dim_date', r);
        EXECUTE format('COMMENT ON VIEW dw.v_dim_%s_date IS %L', r, 'Bản đóng vai (role-playing) của dim_date: ngày ' || r);
    END LOOP;
END $$;

-- ---------------------------------------------------------------- metadata (Vietnamese comments)
DO $$
DECLARE
    r record;
BEGIN
    FOR r IN SELECT * FROM (VALUES
        ('dim_date', NULL, 'Chiều thời gian: 1 dòng / ngày từ 2016-01-01 đến 2020-12-31 (+ dòng Unknown key -1). Dùng chung cho nhiều vai trò (ngày mua, duyệt, giao...)'),
        ('dim_date', 'date_key', 'Khoá ngày dạng số yyyymmdd (vd 20171124); -1 = Unknown'),
        ('dim_date', 'full_date', 'Ngày dạng date'), ('dim_date', 'day_of_month', 'Ngày trong tháng (1-31)'),
        ('dim_date', 'day_of_week', 'Thứ trong tuần, 1 = Thứ Hai ... 7 = Chủ Nhật'), ('dim_date', 'day_name', 'Tên thứ (tiếng Anh)'),
        ('dim_date', 'week_of_year', 'Số tuần theo chuẩn ISO'), ('dim_date', 'month', 'Tháng (1-12)'), ('dim_date', 'month_name', 'Tên tháng'),
        ('dim_date', 'quarter', 'Quý (1-4)'), ('dim_date', 'year', 'Năm'), ('dim_date', 'year_month', 'Năm-tháng, vd 2017-11'),
        ('dim_date', 'year_quarter', 'Năm-quý, vd 2017-Q4'), ('dim_date', 'is_weekend', 'Cuối tuần (Thứ Bảy, Chủ Nhật)'),
        ('dim_date', 'is_holiday_br', 'Ngày lễ quốc gia của Brazil'), ('dim_date', 'holiday_name', 'Tên ngày lễ'),
        ('dim_date', 'is_black_friday', 'Black Friday (thứ Sáu sau thứ Năm thứ 4 của tháng 11)'),
        ('dim_geography', NULL, 'Chiều địa lý: 1 dòng / mã bưu chính (zip prefix); phân cấp Zip - Thành phố - Bang - Vùng - Quốc gia'),
        ('dim_geography', 'geography_key', 'Khoá thay thế'), ('dim_geography', 'zip_code_prefix', 'Mã bưu chính 5 số (khoá tự nhiên)'),
        ('dim_geography', 'city', 'Tên thành phố đã chuẩn hoá (chữ thường, không dấu)'), ('dim_geography', 'state_code', 'Mã bang 2 ký tự'),
        ('dim_geography', 'state_name', 'Tên bang'), ('dim_geography', 'region', 'Vùng: Norte, Nordeste, Centro-Oeste, Sudeste, Sul'),
        ('dim_geography', 'country', 'Quốc gia'), ('dim_geography', 'latitude', 'Vĩ độ (median của zip); NULL nếu zip không có trong bảng toạ độ'),
        ('dim_geography', 'longitude', 'Kinh độ (median của zip); NULL nếu zip không có trong bảng toạ độ'),
        ('dim_customer', NULL, 'Chiều khách hàng, SCD loại 2: 1 dòng / phiên bản địa chỉ của 1 khách thật (customer_unique_id)'),
        ('dim_customer', 'customer_key', 'Khoá thay thế (mỗi phiên bản một khoá)'), ('dim_customer', 'customer_unique_id', 'Mã khách thật (khoá tự nhiên)'),
        ('dim_customer', 'zip_code_prefix', 'Zip của phiên bản (thuộc tính theo dõi SCD2)'), ('dim_customer', 'city', 'Thành phố của phiên bản'),
        ('dim_customer', 'state_code', 'Bang của phiên bản'), ('dim_customer', 'geography_key', 'Khoá sang dim_geography'),
        ('dim_customer', 'effective_from', 'Ngày bắt đầu hiệu lực (phiên bản đầu = 1900-01-01)'),
        ('dim_customer', 'effective_to', 'Ngày kết thúc hiệu lực (phiên bản hiện hành = 9999-12-31)'),
        ('dim_customer', 'is_current', 'Phiên bản hiện hành'), ('dim_customer', 'version_no', 'Số thứ tự phiên bản của khách (1, 2, ...)'),
        ('dim_seller', NULL, 'Chiều người bán, SCD loại 1, chiều dùng chung (conformed) cho bán hàng và thu hút seller'),
        ('dim_seller', 'seller_key', 'Khoá thay thế'), ('dim_seller', 'seller_id', 'Mã seller (khoá tự nhiên)'),
        ('dim_seller', 'zip_code_prefix', 'Zip của seller (NULL nếu seller chỉ có trong CRM)'), ('dim_seller', 'city', 'Thành phố của seller'),
        ('dim_seller', 'state_code', 'Bang của seller'), ('dim_seller', 'geography_key', 'Khoá sang dim_geography (-1 nếu chưa biết)'),
        ('dim_seller', 'is_from_funnel', 'Seller có trong closed_deals của CRM'), ('dim_seller', 'mql_id', 'MQL đã dẫn tới seller; NULL nếu không từ funnel'),
        ('dim_seller', 'acquisition_origin', 'Kênh gốc của MQL; not_from_funnel nếu seller không từ funnel'),
        ('dim_seller', 'acquisition_channel', 'Nhóm kênh thu hút (Organic, Paid, Social, Email, Other, Unknown, Not from funnel)'),
        ('dim_seller', 'business_segment', 'Phân khúc kinh doanh khai báo khi chốt deal'), ('dim_seller', 'lead_type', 'Loại lead'),
        ('dim_seller', 'business_type', 'Loại hình kinh doanh'), ('dim_seller', 'won_date', 'Ngày chốt deal'),
        ('dim_seller', 'first_sale_date', 'Ngày mua của đơn đầu tiên không thuộc nhóm Failed của seller (cập nhật sau khi nạp fact_order_item); NULL nếu mọi đơn đều Failed'),
        ('dim_product', NULL, 'Chiều sản phẩm: 1 dòng / sản phẩm; phân cấp Sản phẩm - Danh mục - Nhóm ngành hàng'),
        ('dim_product', 'product_key', 'Khoá thay thế'), ('dim_product', 'product_id', 'Mã sản phẩm (khoá tự nhiên)'),
        ('dim_product', 'category_name_pt', 'Tên danh mục tiếng Bồ Đào Nha (unknown nếu rỗng)'), ('dim_product', 'category_name_en', 'Tên danh mục tiếng Anh'),
        ('dim_product', 'category_group', 'Nhóm ngành hàng (13 nhóm, từ seeds/category_group.csv)'), ('dim_product', 'weight_g', 'Cân nặng (gram)'),
        ('dim_product', 'length_cm', 'Chiều dài (cm)'), ('dim_product', 'height_cm', 'Chiều cao (cm)'), ('dim_product', 'width_cm', 'Chiều rộng (cm)'),
        ('dim_product', 'volume_cm3', 'Thể tích = dài x cao x rộng (cm3)'),
        ('dim_product', 'size_class', 'Cỡ hàng: S (<500 g), M (<2 kg), L (<10 kg), XL (>=10 kg), Unknown'),
        ('dim_product', 'photos_qty', 'Số ảnh'), ('dim_product', 'name_length', 'Độ dài tên sản phẩm (ký tự)'), ('dim_product', 'description_length', 'Độ dài mô tả (ký tự)'),
        ('dim_order_status', NULL, 'Chiều trạng thái đơn: 8 trạng thái + Unknown'), ('dim_order_status', 'order_status', 'Trạng thái gốc'),
        ('dim_order_status', 'status_group', 'Nhóm: Completed, In progress, Failed'), ('dim_order_status', 'is_final', 'Trạng thái cuối (không đổi nữa)'),
        ('dim_payment_type', NULL, 'Chiều hình thức thanh toán'), ('dim_payment_type', 'payment_type', 'Loại gốc (credit_card, boleto, ...)'),
        ('dim_payment_type', 'payment_group', 'Nhóm (Card, Bank slip, Voucher, Unknown)'), ('dim_payment_type', 'display_name', 'Tên hiển thị'),
        ('dim_lead_origin', NULL, 'Chiều kênh thu hút của MQL'), ('dim_lead_origin', 'origin', 'Kênh gốc (organic_search, paid_search, ...)'),
        ('dim_lead_origin', 'channel_group', 'Nhóm kênh: Organic, Paid, Social, Email, Other, Unknown'),
        ('dim_lead_profile', NULL, 'Chiều hồ sơ deal (junk dimension): mỗi tổ hợp thuộc tính deal một dòng; dòng -1 cho MQL chưa chốt'),
        ('dim_lead_profile', 'business_segment', 'Phân khúc kinh doanh'), ('dim_lead_profile', 'lead_type', 'Loại lead'),
        ('dim_lead_profile', 'lead_behaviour_profile', 'Hồ sơ hành vi'), ('dim_lead_profile', 'business_type', 'Loại hình kinh doanh'),
        ('dim_lead_profile', 'has_company', 'Có công ty (true/false/unknown)'), ('dim_lead_profile', 'has_gtin', 'Có mã GTIN (true/false/unknown)'),
        ('dim_lead_profile', 'average_stock', 'Tồn kho trung bình khai báo'),
        ('dim_sales_rep', NULL, 'Chiều nhân viên sales, đóng 2 vai trò: SDR (tìm khách) và SR (chốt deal)'),
        ('dim_sales_rep', 'rep_id', 'Mã nhân viên'), ('dim_sales_rep', 'rep_role', 'Vai trò: SDR hoặc SR')
    ) AS t(tbl, col, cmt)
    LOOP
        IF r.col IS NULL THEN
            EXECUTE format('COMMENT ON TABLE dw.%I IS %L', r.tbl, r.cmt);
        ELSE
            EXECUTE format('COMMENT ON COLUMN dw.%I.%I IS %L', r.tbl, r.col, r.cmt);
        END IF;
    END LOOP;
END $$;
