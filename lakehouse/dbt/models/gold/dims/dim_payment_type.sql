select cast(row_number() over (order by payment_type) as integer) as payment_type_key, payment_type, payment_group, display_name
from {{ ref('payment_type') }}
union all
select -1, 'unknown', 'Unknown', 'Unknown'
