-- depends_on: {{ ref('dim_date') }}
{# transaction fact, grain = order item; same lookups and Unknown member (-1) as dw.load_fact_order_item #}
select i.order_id, i.order_item_id,
       {{ date_key(ts('o.order_purchase_timestamp')) }} as purchase_date_key,
       {{ date_key(ts('i.shipping_limit_date')) }} as shipping_limit_date_key,
       coalesce(dc.customer_key, -1) as customer_key, coalesce(dc.geography_key, -1) as customer_geography_key,
       coalesce(s.geography_key, -1) as seller_geography_key, coalesce(s.seller_key, -1) as seller_key,
       coalesce(p.product_key, -1) as product_key, coalesce(os.order_status_key, -1) as order_status_key,
       i.price, i.freight_value, i.price + i.freight_value as item_total
from {{ source('silver', 'order_items') }} i
join {{ source('silver', 'orders') }} o on o.order_id = i.order_id
join {{ source('silver', 'customers') }} c on c.customer_id = o.customer_id
left join {{ ref('dim_customer') }} dc on dc.customer_unique_id = c.customer_unique_id
     and cast(o.order_purchase_timestamp as date) between dc.effective_from and dc.effective_to
left join {{ ref('dim_seller') }} s on s.seller_id = i.seller_id
left join {{ ref('dim_product') }} p on p.product_id = i.product_id
left join {{ ref('dim_order_status') }} os on os.order_status = o.order_status
