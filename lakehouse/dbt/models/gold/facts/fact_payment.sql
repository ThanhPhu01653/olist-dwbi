-- depends_on: {{ ref('dim_date') }}
{# transaction fact, grain = payment of an order #}
select p.order_id, p.payment_sequential, {{ date_key(ts('o.order_purchase_timestamp')) }} as purchase_date_key,
       coalesce(dc.customer_key, -1) as customer_key, coalesce(pt.payment_type_key, -1) as payment_type_key,
       p.payment_installments, p.payment_value
from {{ source('silver', 'order_payments') }} p
join {{ source('silver', 'orders') }} o on o.order_id = p.order_id
join {{ source('silver', 'customers') }} c on c.customer_id = o.customer_id
left join {{ ref('dim_customer') }} dc on dc.customer_unique_id = c.customer_unique_id
     and cast(o.order_purchase_timestamp as date) between dc.effective_from and dc.effective_to
left join {{ ref('dim_payment_type') }} pt on pt.payment_type = p.payment_type
