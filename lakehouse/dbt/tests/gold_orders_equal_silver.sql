-- custom test: one row per Silver order in fact_order_fulfillment, and its order_value adds up to the items
select 1 as failed
from (select count(*) as n, sum(order_value) as v from {{ ref('fact_order_fulfillment') }}) g
cross join (select count(*) as n from {{ source('silver', 'orders') }}) s
cross join (select sum(price) as v from {{ source('silver', 'order_items') }}) i
where g.n <> s.n or g.v <> i.v
