-- setup: required
-- Data mart "customer experience": reviews vs delay, payment mix, RFM and cohort (customer = customer_unique_id).
-- RFM and cohort use orders that are not 'Failed' and have at least one item; they are MATERIALIZED (refreshed by dw.refresh_marts).

CREATE OR REPLACE VIEW mart_cx.v_review_vs_delay AS
SELECT d.year_month, (d.year_month BETWEEN '2017-01' AND '2018-08') AS in_window,
       CASE WHEN o.delay_days < 0 THEN 1 WHEN o.delay_days = 0 THEN 2 WHEN o.delay_days <= 3 THEN 3 WHEN o.delay_days <= 7 THEN 4 ELSE 5 END AS delay_bucket_no,
       CASE WHEN o.delay_days < 0 THEN 'Giao sớm' WHEN o.delay_days = 0 THEN 'Đúng ngày dự kiến' WHEN o.delay_days <= 3 THEN 'Trễ 1-3 ngày'
            WHEN o.delay_days <= 7 THEN 'Trễ 4-7 ngày' ELSE 'Trễ trên 7 ngày' END AS delay_bucket,
       count(*) AS reviews, sum(r.review_score) AS score_sum, sum(r.is_negative) AS negative_reviews,
       round(avg(r.review_score), 3) AS avg_score, round(100.0 * avg(r.is_negative), 2) AS pct_negative,
       round(avg(r.response_hours), 1) AS avg_response_hours
FROM dw.fact_review r
JOIN dw.fact_order_fulfillment o ON o.order_id = r.order_id AND o.is_delivered = 1 AND o.delay_days IS NOT NULL
JOIN dw.dim_date d ON d.date_key = o.purchase_date_key
GROUP BY d.year_month, 3, 4;

CREATE OR REPLACE VIEW mart_cx.v_payment_mix_month AS
SELECT d.year_month, (d.year_month BETWEEN '2017-01' AND '2018-08') AS in_window, pt.payment_type, pt.payment_group, pt.display_name,
       count(*) AS payments, count(DISTINCT f.order_id) AS orders, sum(f.payment_value) AS payment_value,
       round(avg(f.payment_installments), 2) AS avg_installments,
       round(100.0 * sum(f.payment_value) / sum(sum(f.payment_value)) OVER (PARTITION BY d.year_month), 2) AS value_share_pct
FROM dw.fact_payment f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key
JOIN dw.dim_payment_type pt ON pt.payment_type_key = f.payment_type_key
GROUP BY d.year_month, pt.payment_type, pt.payment_group, pt.display_name;

DROP MATERIALIZED VIEW IF EXISTS mart_cx.v_customer_rfm;
CREATE MATERIALIZED VIEW mart_cx.v_customer_rfm AS
WITH o AS (
    SELECT c.customer_unique_id AS uid, f.order_id, f.purchase_ts::date AS pd, f.order_value + f.freight_total AS val
    FROM dw.fact_order_fulfillment f
    JOIN dw.dim_customer c ON c.customer_key = f.customer_key
    JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key
    WHERE s.status_group <> 'Failed' AND f.item_count > 0 AND c.customer_key <> -1),
snap AS (SELECT max(pd) + 1 AS d FROM o),
a AS (
    SELECT uid, min(pd) AS first_purchase, max(pd) AS last_purchase, count(*) AS frequency, sum(val) AS monetary
    FROM o GROUP BY uid),
s AS (
    SELECT a.*, (snap.d - a.last_purchase) AS recency_days,
           ntile(5) OVER (ORDER BY (snap.d - a.last_purchase) DESC) AS r_score,
           CASE WHEN a.frequency = 1 THEN 1 WHEN a.frequency = 2 THEN 3 ELSE 5 END AS f_score,
           ntile(5) OVER (ORDER BY a.monetary) AS m_score
    FROM a CROSS JOIN snap),
cur AS (SELECT DISTINCT ON (customer_unique_id) customer_unique_id, geography_key FROM dw.dim_customer WHERE customer_key <> -1
        ORDER BY customer_unique_id, effective_from DESC)
SELECT s.uid AS customer_unique_id, g.region, g.state_code, s.first_purchase, s.last_purchase, s.recency_days, s.frequency, round(s.monetary, 2) AS monetary,
       s.r_score, s.f_score, s.m_score,
       CASE WHEN s.f_score = 5 AND s.r_score >= 4 THEN 'Champions'
            WHEN s.f_score >= 3 AND s.r_score >= 4 THEN 'Khách trung thành'
            WHEN s.f_score >= 3 THEN 'Có nguy cơ rời bỏ'
            WHEN s.r_score >= 4 THEN 'Khách mới'
            WHEN s.r_score = 3 THEN 'Cần giữ chân'
            ELSE 'Ngủ đông' END AS segment
FROM s JOIN cur ON cur.customer_unique_id = s.uid JOIN dw.dim_geography g ON g.geography_key = cur.geography_key;
CREATE UNIQUE INDEX ON mart_cx.v_customer_rfm (customer_unique_id);

DROP MATERIALIZED VIEW IF EXISTS mart_cx.v_customer_cohort;
CREATE MATERIALIZED VIEW mart_cx.v_customer_cohort AS
WITH o AS (
    SELECT DISTINCT c.customer_unique_id AS uid, date_trunc('month', f.purchase_ts)::date AS m
    FROM dw.fact_order_fulfillment f
    JOIN dw.dim_customer c ON c.customer_key = f.customer_key
    JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key
    WHERE s.status_group <> 'Failed' AND f.item_count > 0 AND c.customer_key <> -1),
fm AS (SELECT uid, min(m) AS cm FROM o GROUP BY uid),
sz AS (SELECT cm, count(*) AS n FROM fm GROUP BY cm),
act AS (
    SELECT fm.cm, ((extract(year FROM o.m) - extract(year FROM fm.cm)) * 12 + extract(month FROM o.m) - extract(month FROM fm.cm))::int AS months_since,
           count(*) AS active
    FROM o JOIN fm USING (uid) GROUP BY fm.cm, 2)
SELECT to_char(act.cm, 'YYYY-MM') AS cohort_month, (to_char(act.cm, 'YYYY-MM') BETWEEN '2017-01' AND '2018-08') AS in_window,
       act.months_since, sz.n AS cohort_size, act.active AS customers_active, round(100.0 * act.active / sz.n, 2) AS retention_pct
FROM act JOIN sz ON sz.cm = act.cm;

COMMENT ON SCHEMA mart_cx IS 'Data mart trải nghiệm khách: review vs trễ, cơ cấu thanh toán, RFM, cohort';
COMMENT ON VIEW mart_cx.v_review_vs_delay IS 'Điểm review và % tiêu cực theo nhóm trễ giao (giao sớm ... trễ trên 7 ngày) x tháng mua; chỉ đơn đã giao';
COMMENT ON VIEW mart_cx.v_payment_mix_month IS 'Cơ cấu thanh toán theo tháng mua x hình thức: số lần, giá trị, trả góp TB, tỷ trọng giá trị';
COMMENT ON MATERIALIZED VIEW mart_cx.v_customer_rfm IS '1 dòng / khách thật (customer_unique_id): recency, frequency, monetary, điểm R-F-M 1-5 và phân khúc; đơn không thuộc nhóm Failed';
COMMENT ON MATERIALIZED VIEW mart_cx.v_customer_cohort IS 'Cohort theo tháng mua đầu tiên: số khách còn mua lại sau 0,1,2... tháng và tỷ lệ quay lại';
