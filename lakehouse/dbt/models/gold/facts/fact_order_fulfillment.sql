{# accumulating snapshot, grain = order. Intervals come from the original timestamps; a negative value (source error) becomes NULL and is counted in
   dq_flag_count on top of the flags Silver already set. Hours and days are rounded in integer arithmetic (half away from zero, like PostgreSQL numeric). #}
with o as (
    select order_id, customer_id, order_status, dq_flag_count as ods_flags,
           {{ ts('order_purchase_timestamp') }} as purchase_ts, {{ ts('order_approved_at') }} as approved_ts, {{ ts('order_delivered_carrier_date') }} as carrier_ts,
           {{ ts('order_delivered_customer_date') }} as delivered_ts, {{ ts('order_estimated_delivery_date') }} as estimated_ts
    from {{ source('silver', 'orders') }}
),
it as (
    select order_id, count(*) as item_count, count(distinct seller_id) as seller_count, sum(price) as order_value, sum(freight_value) as freight_total
    from {{ source('silver', 'order_items') }} group by order_id
),
pm as (select order_id, sum(payment_value) as payment_total from {{ source('silver', 'order_payments') }} group by order_id),
base as (
    select o.order_id, o.order_status, o.ods_flags, o.purchase_ts, o.approved_ts, o.carrier_ts, o.delivered_ts, o.estimated_ts,
           coalesce(dc.customer_key, -1) as customer_key, coalesce(dc.geography_key, -1) as customer_geography_key, coalesce(os.order_status_key, -1) as order_status_key,
           {{ secs('o.purchase_ts', 'o.approved_ts') }} as approval_s, {{ secs('o.approved_ts', 'o.carrier_ts') }} as handling_s,
           {{ secs('o.carrier_ts', 'o.delivered_ts') }} as transit_s, {{ secs('o.purchase_ts', 'o.delivered_ts') }} as lead_s,
           date_diff('day', cast(o.estimated_ts as date), cast(o.delivered_ts as date)) as delay_days,
           date_diff('day', cast(o.purchase_ts as date), cast(o.estimated_ts as date)) as promised_raw,
           coalesce(it.item_count, 0) as item_count, coalesce(it.seller_count, 0) as seller_count, coalesce(it.order_value, 0) as order_value,
           coalesce(it.freight_total, 0) as freight_total, coalesce(pm.payment_total, 0) as payment_total
    from o
    join {{ source('silver', 'customers') }} c on c.customer_id = o.customer_id
    left join {{ ref('dim_customer') }} dc on dc.customer_unique_id = c.customer_unique_id and cast(o.purchase_ts as date) between dc.effective_from and dc.effective_to
    left join {{ ref('dim_order_status') }} os on os.order_status = o.order_status
    left join it on it.order_id = o.order_id
    left join pm on pm.order_id = o.order_id
),
b2 as (
    select base.*, case when order_status = 'delivered' and delivered_ts is not null then 1 else 0 end as is_delivered,
           (case when approval_s < 0 then 1 else 0 end) + (case when handling_s < 0 then 1 else 0 end) + (case when transit_s < 0 then 1 else 0 end)
           + (case when lead_s < 0 then 1 else 0 end) + (case when promised_raw < 0 then 1 else 0 end) as neg_count
    from base
)
select order_id, customer_key, customer_geography_key, order_status_key,
       {{ date_key('purchase_ts') }} as purchase_date_key, {{ date_key('approved_ts') }} as approved_date_key, {{ date_key('carrier_ts') }} as carrier_date_key,
       {{ date_key('delivered_ts') }} as delivered_date_key, {{ date_key('estimated_ts') }} as estimated_date_key,
       purchase_ts, approved_ts, carrier_ts, delivered_ts, estimated_ts,
       case when approval_s >= 0 then {{ round2('approval_s', 3600) }} end as approval_hours,
       case when handling_s >= 0 then {{ round2('handling_s', 86400) }} end as handling_days,
       case when transit_s >= 0 then {{ round2('transit_s', 86400) }} end as transit_days,
       case when lead_s >= 0 then {{ round2('lead_s', 86400) }} end as lead_days,
       delay_days, case when promised_raw >= 0 then promised_raw end as promised_days,
       is_delivered, case when is_delivered = 1 and delay_days > 0 then 1 else 0 end as is_late, case when order_status = 'canceled' then 1 else 0 end as is_canceled,
       item_count, seller_count, order_value, freight_total, payment_total, ods_flags + neg_count as dq_flag_count
from b2
