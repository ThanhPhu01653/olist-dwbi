select d.year_month, d.year, d.quarter, (d.year_month between '2017-01' and '2018-08') as in_window, p.category_group, p.category_name_en,
       count(distinct f.order_id) as orders, count(*) as items, sum(f.price) as gmv, sum(f.freight_value) as freight, round(sum(f.price) / count(*), 2) as avg_item_price
from {{ ref('fact_order_item') }} f
join {{ ref('dim_date') }} d on d.date_key = f.purchase_date_key
join {{ ref('dim_product') }} p on p.product_key = f.product_key
join {{ ref('dim_order_status') }} s on s.order_status_key = f.order_status_key and s.status_group <> 'Failed'
group by d.year_month, d.year, d.quarter, p.category_group, p.category_name_en
