with p as (
    select distinct business_segment, lead_type, lead_behaviour_profile, business_type, has_company, has_gtin, average_stock
    from {{ source('silver', 'closed_deals') }}
)
select cast(row_number() over (order by business_segment, lead_type, lead_behaviour_profile, business_type, has_company, has_gtin, average_stock) as integer) as lead_profile_key,
       business_segment, lead_type, lead_behaviour_profile, business_type, has_company, has_gtin, average_stock
from p
union all
select -1, 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a'
