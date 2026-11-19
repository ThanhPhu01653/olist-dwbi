{# periodic snapshot, grain = seller x month, dense grid from the first month with an item to the last month of the data #}
with it as (
    select f.seller_key, date_trunc('month', dd.full_date) as m, f.order_id, f.price, f.freight_value, os.status_group
    from {{ ref('fact_order_item') }} f
    join {{ ref('dim_date') }} dd on dd.date_key = f.purchase_date_key
    join {{ ref('dim_order_status') }} os on os.order_status_key = f.order_status_key
    where f.seller_key <> -1 and f.purchase_date_key <> -1
),
ord as (
    select i.seller_key, i.m, i.order_id, coalesce(max(fo.is_delivered), 0) as is_delivered, coalesce(max(fo.is_late), 0) as is_late, coalesce(max(fo.is_canceled), 0) as is_canceled
    from it i left join {{ ref('fact_order_fulfillment') }} fo on fo.order_id = i.order_id
    group by i.seller_key, i.m, i.order_id
),
sel as (select seller_key, min(m) as first_m from it group by seller_key),
lastm as (select max(m) as last_m from it),
grid as (select s.seller_key, g.m from sel s cross join lastm l cross join unnest(sequence(s.first_m, l.last_m, interval '1' month)) as g(m)),
a_it as (
    select seller_key, m, count(*) as items, sum(price) filter (where status_group <> 'Failed') as gmv, sum(freight_value) filter (where status_group <> 'Failed') as freight
    from it group by seller_key, m
),
a_ord as (
    select seller_key, m, count(*) as orders, sum(is_delivered) as delivered_orders, sum(is_late) as late_orders, sum(is_canceled) as canceled_orders
    from ord group by seller_key, m
),
a_rev as (
    select o.seller_key, o.m, avg(cast(r.review_score as decimal(10, 4))) as avg_score
    from ord o join {{ ref('fact_review') }} r on r.order_id = o.order_id group by o.seller_key, o.m
)
select cast(date_format(g.m, '%Y%m%d') as integer) as month_date_key, g.seller_key,
       cast(coalesce(ao.orders, 0) as integer) as orders, cast(coalesce(ai.items, 0) as integer) as items, coalesce(ai.gmv, 0) as gmv, coalesce(ai.freight, 0) as freight,
       cast(coalesce(ao.delivered_orders, 0) as integer) as delivered_orders, cast(coalesce(ao.late_orders, 0) as integer) as late_orders,
       case when ao.delivered_orders > 0 then round(cast(ao.late_orders as decimal(18, 4)) / ao.delivered_orders, 4) end as late_rate,
       cast(coalesce(ao.canceled_orders, 0) as integer) as canceled_orders, round(ar.avg_score, 2) as avg_review_score,
       case when coalesce(ao.orders, 0) > 0 then 1 else 0 end as is_active,
       case when ds.first_sale_date is not null then cast((year(g.m) - year(ds.first_sale_date)) * 12 + month(g.m) - month(ds.first_sale_date) as integer) end as months_since_first_sale
from grid g
join {{ ref('dim_seller') }} ds on ds.seller_key = g.seller_key
left join a_it ai on ai.seller_key = g.seller_key and ai.m = g.m
left join a_ord ao on ao.seller_key = g.seller_key and ao.m = g.m
left join a_rev ar on ar.seller_key = g.seller_key and ar.m = g.m
