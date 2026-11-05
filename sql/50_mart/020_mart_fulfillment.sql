-- setup: required
-- Data mart "fulfillment": order lead times per stage, late and cancel rates. Counts every placed order unless stated.

CREATE OR REPLACE VIEW mart_fulfillment.v_fulfillment_order AS
SELECT o.order_id, dp.full_date AS purchase_date, dp.year_month, (dp.year_month BETWEEN '2017-01' AND '2018-08') AS in_window,
       os.order_status, os.status_group, g.region AS customer_region, g.state_code AS customer_state, g.city AS customer_city,
       da.full_date AS approved_date, dc.full_date AS carrier_date, dd.full_date AS delivered_date, de.full_date AS estimated_date,
       o.approval_hours, o.handling_days, o.transit_days, o.lead_days, o.promised_days, o.delay_days,
       o.is_delivered, o.is_late, o.is_canceled, o.item_count, o.seller_count, o.order_value, o.freight_total, o.payment_total, o.dq_flag_count,
       CASE WHEN o.is_delivered = 0 THEN 'Chưa giao' WHEN o.delay_days < 0 THEN 'Giao sớm' WHEN o.delay_days = 0 THEN 'Đúng ngày dự kiến'
            WHEN o.delay_days <= 3 THEN 'Trễ 1-3 ngày' WHEN o.delay_days <= 7 THEN 'Trễ 4-7 ngày' ELSE 'Trễ trên 7 ngày' END AS delay_bucket,
       CASE WHEN o.is_delivered = 0 THEN 0 WHEN o.delay_days < 0 THEN 1 WHEN o.delay_days = 0 THEN 2 WHEN o.delay_days <= 3 THEN 3
            WHEN o.delay_days <= 7 THEN 4 ELSE 5 END AS delay_bucket_no
FROM dw.fact_order_fulfillment o
JOIN dw.dim_date dp ON dp.date_key = o.purchase_date_key
JOIN dw.dim_date da ON da.date_key = o.approved_date_key
JOIN dw.dim_date dc ON dc.date_key = o.carrier_date_key
JOIN dw.dim_date dd ON dd.date_key = o.delivered_date_key
JOIN dw.dim_date de ON de.date_key = o.estimated_date_key
JOIN dw.dim_order_status os ON os.order_status_key = o.order_status_key
JOIN dw.dim_geography g ON g.geography_key = o.customer_geography_key;

CREATE OR REPLACE VIEW mart_fulfillment.v_fulfillment_state_month AS
SELECT d.year_month, (d.year_month BETWEEN '2017-01' AND '2018-08') AS in_window, g.region, g.state_code,
       count(*) AS orders, sum(o.is_delivered) AS delivered_orders, sum(o.is_late) AS late_orders, sum(o.is_canceled) AS canceled_orders,
       round(100.0 * (sum(o.is_delivered) - sum(o.is_late)) / nullif(sum(o.is_delivered), 0), 2) AS on_time_rate_pct,
       round(100.0 * sum(o.is_canceled) / count(*), 2) AS cancel_rate_pct,
       round(avg(o.lead_days) FILTER (WHERE o.is_delivered = 1), 2) AS avg_lead_days,
       round(avg(o.approval_hours) FILTER (WHERE o.is_delivered = 1), 2) AS avg_approval_hours,
       round(avg(o.handling_days) FILTER (WHERE o.is_delivered = 1), 2) AS avg_handling_days,
       round(avg(o.transit_days) FILTER (WHERE o.is_delivered = 1), 2) AS avg_transit_days,
       round(avg(o.promised_days) FILTER (WHERE o.is_delivered = 1), 2) AS avg_promised_days
FROM dw.fact_order_fulfillment o
JOIN dw.dim_date d ON d.date_key = o.purchase_date_key
JOIN dw.dim_geography g ON g.geography_key = o.customer_geography_key
GROUP BY d.year_month, g.region, g.state_code;

-- Long format: how many orders reach each stage of the pipeline, per purchase month
CREATE OR REPLACE VIEW mart_fulfillment.v_status_funnel AS
WITH p AS (
    SELECT d.year_month, count(*) AS placed, count(*) FILTER (WHERE o.approved_date_key <> -1) AS approved,
           count(*) FILTER (WHERE o.carrier_date_key <> -1) AS carrier, count(*) FILTER (WHERE o.is_delivered = 1) AS delivered,
           count(*) FILTER (WHERE o.is_canceled = 1) AS canceled
    FROM dw.fact_order_fulfillment o JOIN dw.dim_date d ON d.date_key = o.purchase_date_key
    GROUP BY d.year_month)
SELECT p.year_month, (p.year_month BETWEEN '2017-01' AND '2018-08') AS in_window, v.stage_no, v.stage, v.orders,
       round(100.0 * v.orders / p.placed, 2) AS pct_of_placed
FROM p CROSS JOIN LATERAL (VALUES (1, 'Đặt hàng', p.placed), (2, 'Đã duyệt thanh toán', p.approved), (3, 'Đã bàn giao vận chuyển', p.carrier),
                                  (4, 'Đã giao khách', p.delivered), (5, 'Bị hủy', p.canceled)) v(stage_no, stage, orders);

COMMENT ON SCHEMA mart_fulfillment IS 'Data mart xử lý đơn: thời gian từng chặng, tỷ lệ giao trễ và hủy';
COMMENT ON VIEW mart_fulfillment.v_fulfillment_order IS '1 dòng / đơn: mốc ngày, thời gian từng chặng, số ngày hứa và trễ, nhóm trễ (delay_bucket), bang và vùng của khách';
COMMENT ON VIEW mart_fulfillment.v_fulfillment_state_month IS 'Theo tháng mua x bang: số đơn, tỷ lệ đúng hạn / hủy, thời gian trung bình từng chặng (chỉ đơn đã giao)';
COMMENT ON VIEW mart_fulfillment.v_status_funnel IS 'Số đơn đi qua từng chặng (đặt, duyệt, bàn giao, giao, hủy) theo tháng mua, dạng dài';
