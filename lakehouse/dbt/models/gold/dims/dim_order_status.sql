select cast(row_number() over (order by order_status) as integer) as order_status_key, order_status, status_group, is_final
from {{ ref('order_status') }}
union all
select -1, 'unknown', 'Unknown', false
