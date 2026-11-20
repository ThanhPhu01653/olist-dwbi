{# conformed seller (sales + CRM); first_sale_date = first purchase date of an order that is not Failed, computed from Silver (no cycle with the fact) #}
with base as (
    select seller_id, zip_code_prefix as zip, city, state_code as st from {{ source('silver', 'sellers') }}
    union all
    select d.seller_id, cast(null as varchar), cast(null as varchar), cast(null as varchar)
    from {{ source('silver', 'closed_deals') }} d where not exists (select 1 from {{ source('silver', 'sellers') }} s where s.seller_id = d.seller_id)
),
fs as (
    select i.seller_id, min(cast(o.order_purchase_timestamp as date)) as first_sale_date
    from {{ source('silver', 'order_items') }} i
    join {{ source('silver', 'orders') }} o on o.order_id = i.order_id
    join {{ ref('order_status') }} os on os.order_status = o.order_status and os.status_group <> 'Failed'
    where cast(o.order_purchase_timestamp as date) between date '2016-01-01' and date '2020-12-31'
    group by i.seller_id
)
select cast(row_number() over (order by t.seller_id) as integer) as seller_key, t.seller_id, t.zip as zip_code_prefix, coalesce(t.city, 'unknown') as city, t.st as state_code,
       coalesce(g.geography_key, -1) as geography_key, d.mql_id is not null as is_from_funnel, d.mql_id,
       coalesce(m.origin, 'not_from_funnel') as acquisition_origin,
       case when d.mql_id is null then 'Not from funnel' else coalesce(og.channel_group, 'Unknown') end as acquisition_channel,
       d.business_segment, d.lead_type, d.business_type, cast(d.won_date as date) as won_date, fs.first_sale_date
from base t
left join {{ ref('dim_geography') }} g on g.zip_code_prefix = t.zip
left join {{ source('silver', 'closed_deals') }} d on d.seller_id = t.seller_id
left join {{ source('silver', 'mql') }} m on m.mql_id = d.mql_id
left join {{ ref('lead_origin_group') }} og on og.origin = m.origin
left join fs on fs.seller_id = t.seller_id
union all
select -1, 'unknown', null, 'unknown', null, -1, false, null, 'not_from_funnel', 'Not from funnel', null, null, null, null, null
