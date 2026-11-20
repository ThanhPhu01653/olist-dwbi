select d.year_month, d.year, d.quarter, (d.year_month between '2017-01' and '2018-08') as in_window, g.region, g.state_code, g.state_name,
       count(distinct f.order_id) as orders, count(*) as items, sum(f.price) as gmv, sum(f.freight_value) as freight,
       round(sum(f.freight_value) / nullif(sum(f.price), 0), 4) as freight_ratio
from {{ ref('fact_order_item') }} f
join {{ ref('dim_date') }} d on d.date_key = f.purchase_date_key
join {{ ref('dim_geography') }} g on g.geography_key = f.customer_geography_key
join {{ ref('dim_order_status') }} s on s.order_status_key = f.order_status_key and s.status_group <> 'Failed'
group by d.year_month, d.year, d.quarter, g.region, g.state_code, g.state_name
