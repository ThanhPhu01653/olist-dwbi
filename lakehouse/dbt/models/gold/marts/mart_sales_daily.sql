select d.date_key, d.full_date, d.year, d.quarter, d.year_month, d.is_weekend, d.is_holiday_br, d.is_black_friday,
       (d.year_month between '2017-01' and '2018-08') as in_window,
       count(distinct f.order_id) as orders, count(*) as items, sum(f.price) as gmv, sum(f.freight_value) as freight,
       round(sum(f.price) / nullif(count(distinct f.order_id), 0), 2) as aov
from {{ ref('fact_order_item') }} f
join {{ ref('dim_date') }} d on d.date_key = f.purchase_date_key
join {{ ref('dim_order_status') }} s on s.order_status_key = f.order_status_key and s.status_group <> 'Failed'
group by d.date_key, d.full_date, d.year, d.quarter, d.year_month, d.is_weekend, d.is_holiday_br, d.is_black_friday
