{# SCD type 2 of the customer address: versions come from silver.customer_address_scd2 (Spark MERGE, logic of dw.load_dim_customer) #}
select cast(row_number() over (order by s.customer_unique_id, s.effective_from) as integer) as customer_key,
       s.customer_unique_id, s.zip_code_prefix, s.city, s.state_code, coalesce(g.geography_key, -1) as geography_key,
       s.effective_from, s.effective_to, s.is_current, s.version_no
from {{ source('silver', 'customer_address_scd2') }} s
left join {{ ref('dim_geography') }} g on g.zip_code_prefix = s.zip_code_prefix
union all
select -1, 'unknown', null, 'unknown', null, -1, date '1900-01-01', date '9999-12-31', true, 1
