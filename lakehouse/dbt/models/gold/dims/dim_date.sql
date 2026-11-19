{# the calendar of the warehouse (seed) + USD/BRL, IPCA index and official holidays of the API data (like dw.enrich_dim_date) #}
with hol as (
    select holiday_date, array_join(array_sort(array_agg(distinct name)), ' / ') as names from {{ source('silver', 'holiday_official') }} group by holiday_date
),
anyhol as (select count(*) as n from {{ source('silver', 'holiday_official') }})
select d.date_key, d.full_date, d.day_of_month, d.day_of_week, d.day_name, d.week_of_year, d.month, d.month_name, d.quarter, d.year, d.year_month, d.year_quarter,
       d.is_weekend, d.is_holiday_br, d.holiday_name, d.is_black_friday,
       f.usd_brl, i.ipca_index, case when (select n from anyhol) > 0 then h.holiday_date is not null end as is_holiday_official, h.names as holiday_name_official
from {{ ref('dim_date_base') }} d
left join {{ source('silver', 'fx_usd_brl') }} f on f.rate_date = d.full_date
left join {{ source('silver', 'ipca_month') }} i on i.month_date = date_trunc('month', d.full_date)
left join hol h on h.holiday_date = d.full_date
union all
select -1, null, null, null, 'Unknown', null, null, 'Unknown', null, null, 'Unknown', 'Unknown', null, null, null, null, null, null, null, null
