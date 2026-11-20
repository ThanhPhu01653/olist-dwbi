-- custom test: the total price of fact_order_item (and its item count) equals Silver order_items; a returned row is a failure
select g.price_sum, s.price_sum as silver_price_sum, g.n, s.n as silver_n
from (select sum(price) as price_sum, count(*) as n from {{ ref('fact_order_item') }}) g
cross join (select sum(i.price) as price_sum, count(*) as n
            from {{ source('silver', 'order_items') }} i join {{ source('silver', 'orders') }} o on o.order_id = i.order_id) s
where g.price_sum <> s.price_sum or g.n <> s.n
