-- setup: required
-- Data mart "acquisition": MQL -> won -> first sale funnel by origin, seller scorecard, sellers by acquisition channel.

-- Funnel by the month of FIRST CONTACT (cohort of leads): how many of them were won, and how many won sellers sold something
CREATE OR REPLACE VIEW mart_acquisition.v_funnel_by_origin_month AS
SELECT d.year_month AS first_contact_month, lo.origin, lo.channel_group,
       count(*) AS mqls, sum(f.is_won) AS won, sum(f.has_first_sale) AS won_with_sale,
       round(100.0 * sum(f.is_won) / count(*), 2) AS win_rate_pct,
       round(100.0 * sum(f.has_first_sale) / nullif(sum(f.is_won), 0), 2) AS won_to_sale_rate_pct,
       round(avg(f.days_to_close), 1) AS avg_days_to_close, round(avg(f.days_won_to_first_sale), 1) AS avg_days_won_to_first_sale,
       coalesce(sum(f.seller_gmv_first_90d), 0) AS seller_gmv_first_90d
FROM dw.fact_lead_funnel f
JOIN dw.dim_date d ON d.date_key = f.first_contact_date_key
JOIN dw.dim_lead_origin lo ON lo.lead_origin_key = f.lead_origin_key
GROUP BY d.year_month, lo.origin, lo.channel_group;

DROP MATERIALIZED VIEW IF EXISTS mart_acquisition.v_seller_by_channel;   -- depends on the scorecard
DROP MATERIALIZED VIEW IF EXISTS mart_acquisition.v_seller_scorecard;
CREATE MATERIALIZED VIEW mart_acquisition.v_seller_scorecard AS
WITH m AS (
    SELECT seller_key, sum(orders) AS orders, sum(items) AS items, sum(gmv) AS gmv, sum(freight) AS freight, sum(delivered_orders) AS delivered_orders,
           sum(late_orders) AS late_orders, sum(canceled_orders) AS canceled_orders, count(*) FILTER (WHERE is_active = 1) AS active_months,
           max(month_date_key) FILTER (WHERE is_active = 1) AS last_active_month_key
    FROM dw.fact_seller_monthly GROUP BY seller_key),
rv AS (
    SELECT so.seller_key, count(*) AS reviews, avg(r.review_score) AS avg_score, avg(r.is_negative) AS neg
    FROM (SELECT DISTINCT seller_key, order_id FROM dw.fact_order_item WHERE seller_key <> -1) so
    JOIN dw.fact_review r ON r.order_id = so.order_id GROUP BY so.seller_key),
b AS (
    SELECT s.seller_key, s.seller_id, s.city, g.state_code, g.region, s.is_from_funnel, s.acquisition_channel, s.acquisition_origin, s.business_segment,
           s.first_sale_date, m.orders, m.items, m.gmv, m.freight, m.delivered_orders, m.late_orders, m.canceled_orders, m.active_months,
           (SELECT d.full_date FROM dw.dim_date d WHERE d.date_key = m.last_active_month_key) AS last_active_month,
           rv.reviews, rv.avg_score, rv.neg
    FROM dw.dim_seller s JOIN m ON m.seller_key = s.seller_key JOIN dw.dim_geography g ON g.geography_key = s.geography_key
    LEFT JOIN rv ON rv.seller_key = s.seller_key),
r AS (
    SELECT b.*, row_number() OVER (ORDER BY gmv DESC, seller_id) AS gmv_rank, 100.0 * gmv / nullif(sum(gmv) OVER (), 0) AS share_pct,
           100.0 * sum(gmv) OVER (ORDER BY gmv DESC, seller_id) / nullif(sum(gmv) OVER (), 0) AS cum_share_pct
    FROM b)
SELECT seller_key, seller_id, city, state_code, region, is_from_funnel, acquisition_channel, acquisition_origin, business_segment, first_sale_date, last_active_month,
       active_months, orders, items, gmv, freight, delivered_orders, late_orders,
       round(100.0 * late_orders / nullif(delivered_orders, 0), 2) AS late_rate_pct, canceled_orders,
       reviews, round(avg_score, 2) AS avg_review_score, round(100.0 * neg, 2) AS pct_negative,
       gmv_rank, round(share_pct, 3) AS gmv_share_pct, round(cum_share_pct, 2) AS cum_share_pct,
       CASE WHEN cum_share_pct - share_pct < 80 THEN 'A' WHEN cum_share_pct - share_pct < 95 THEN 'B' ELSE 'C' END AS abc_class,
       (orders < 10) AS small_sample
FROM r;
CREATE UNIQUE INDEX ON mart_acquisition.v_seller_scorecard (seller_key);

-- Sellers by acquisition channel (every channel incl. 'Not from funnel'); channels with < 30 selling sellers are flagged small_sample
CREATE MATERIALIZED VIEW mart_acquisition.v_seller_by_channel AS
SELECT s.acquisition_channel, count(*) AS sellers, count(c.seller_key) AS selling_sellers,
       round(100.0 * count(c.seller_key) / count(*), 2) AS pct_selling,
       coalesce(sum(c.orders), 0) AS orders, coalesce(sum(c.gmv), 0) AS gmv,
       round(coalesce(sum(c.gmv), 0) / nullif(count(c.seller_key), 0), 2) AS gmv_per_selling_seller,
       round(100.0 * sum(c.late_orders) / nullif(sum(c.delivered_orders), 0), 2) AS late_rate_pct,
       round(sum(c.avg_review_score * c.reviews) / nullif(sum(c.reviews), 0), 2) AS avg_review_score,
       (count(c.seller_key) < 30) AS small_sample
FROM dw.dim_seller s LEFT JOIN mart_acquisition.v_seller_scorecard c ON c.seller_key = s.seller_key
WHERE s.seller_key <> -1
GROUP BY s.acquisition_channel;

COMMENT ON SCHEMA mart_acquisition IS 'Data mart thu hút seller: funnel MQL -> won -> đơn đầu, scorecard seller, seller theo kênh';
COMMENT ON VIEW mart_acquisition.v_funnel_by_origin_month IS 'Funnel theo tháng liên hệ đầu x origin: MQL, đã chốt, đã có đơn, tỷ lệ, số ngày TB, GMV 90 ngày đầu';
COMMENT ON MATERIALIZED VIEW mart_acquisition.v_seller_scorecard IS '1 dòng / seller có đơn: GMV, đơn, trễ, hủy, review, hạng và tỷ trọng luỹ kế (Pareto), cờ mẫu nhỏ (< 10 đơn)';
COMMENT ON MATERIALIZED VIEW mart_acquisition.v_seller_by_channel IS 'Theo kênh thu hút seller: số seller, số seller có đơn, GMV, GMV / seller, trễ, review; cờ mẫu nhỏ (< 30 seller có đơn)';
