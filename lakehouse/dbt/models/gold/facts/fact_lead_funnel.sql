{# accumulating snapshot, grain = MQL; recomputed completely (like dw.load_fact_lead_funnel) #}
with gmv90 as (
    select f.seller_key, sum(f.price) as gmv
    from {{ ref('fact_order_item') }} f
    join {{ ref('dim_seller') }} s on s.seller_key = f.seller_key and s.first_sale_date is not null and s.is_from_funnel
    join {{ ref('dim_date') }} dd on dd.date_key = f.purchase_date_key
    join {{ ref('dim_order_status') }} os on os.order_status_key = f.order_status_key and os.status_group <> 'Failed'
    where dd.full_date >= s.first_sale_date and dd.full_date < date_add('day', 90, s.first_sale_date)
    group by f.seller_key
),
t as (
    select m.mql_id, m.landing_page_id, {{ date_key('cast(m.first_contact_date as timestamp(6))') }} as first_contact_date_key,
           case when d.mql_id is null then -1 else {{ date_key(ts('d.won_date')) }} end as won_date_key,
           case when s.first_sale_date is null then -1 else {{ date_key('cast(s.first_sale_date as timestamp(6))') }} end as first_sale_date_key,
           coalesce(lo.lead_origin_key, -1) as lead_origin_key, coalesce(lp.lead_profile_key, -1) as lead_profile_key,
           coalesce(s.seller_key, -1) as seller_key, coalesce(sdr.sales_rep_key, -1) as sdr_key, coalesce(sr.sales_rep_key, -1) as sr_key,
           case when d.mql_id is not null then 1 else 0 end as is_won, case when s.first_sale_date is not null then 1 else 0 end as has_first_sale,
           date_diff('day', m.first_contact_date, cast(d.won_date as date)) as close_raw, date_diff('day', cast(d.won_date as date), s.first_sale_date) as sale_raw,
           d.declared_product_catalog_size, d.declared_monthly_revenue,
           case when s.first_sale_date is null then null else coalesce(g.gmv, 0) end as seller_gmv_first_90d
    from {{ source('silver', 'mql') }} m
    left join {{ ref('dim_lead_origin') }} lo on lo.origin = m.origin
    left join {{ source('silver', 'closed_deals') }} d on d.mql_id = m.mql_id
    left join {{ ref('dim_seller') }} s on s.seller_id = d.seller_id
    left join {{ ref('dim_lead_profile') }} lp on lp.business_segment = d.business_segment and lp.lead_type = d.lead_type
         and lp.lead_behaviour_profile = d.lead_behaviour_profile and lp.business_type = d.business_type
         and lp.has_company = d.has_company and lp.has_gtin = d.has_gtin and lp.average_stock = d.average_stock
    left join {{ ref('dim_sales_rep') }} sdr on sdr.rep_id = d.sdr_id and sdr.rep_role = 'SDR'
    left join {{ ref('dim_sales_rep') }} sr on sr.rep_id = d.sr_id and sr.rep_role = 'SR'
    left join gmv90 g on g.seller_key = s.seller_key
)
select mql_id, landing_page_id, first_contact_date_key, won_date_key, first_sale_date_key, lead_origin_key, lead_profile_key, seller_key, sdr_key, sr_key,
       is_won, has_first_sale, case when close_raw >= 0 then close_raw end as days_to_close, case when sale_raw >= 0 then sale_raw end as days_won_to_first_sale,
       declared_product_catalog_size, declared_monthly_revenue, seller_gmv_first_90d
from t
