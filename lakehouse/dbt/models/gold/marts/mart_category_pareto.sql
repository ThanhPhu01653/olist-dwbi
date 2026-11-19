with c as (
    select p.category_group, p.category_name_en, sum(f.price) as gmv, count(distinct f.order_id) as orders, count(*) as items
    from {{ ref('fact_order_item') }} f
    join {{ ref('dim_product') }} p on p.product_key = f.product_key
    join {{ ref('dim_order_status') }} s on s.order_status_key = f.order_status_key and s.status_group <> 'Failed'
    group by p.category_group, p.category_name_en
),
r as (
    select c.*, row_number() over (order by gmv desc, category_name_en) as gmv_rank,
           100.0 * gmv / sum(gmv) over () as share_pct,
           100.0 * sum(gmv) over (order by gmv desc, category_name_en) / sum(gmv) over () as cum_share_pct
    from c
)
select gmv_rank, category_group, category_name_en, orders, items, gmv, round(share_pct, 2) as share_pct, round(cum_share_pct, 2) as cum_share_pct,
       case when cum_share_pct - share_pct < 80 then 'A' when cum_share_pct - share_pct < 95 then 'B' else 'C' end as abc_class
from r
