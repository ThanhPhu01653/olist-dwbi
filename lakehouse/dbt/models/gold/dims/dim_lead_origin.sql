select cast(row_number() over (order by origin) as integer) as lead_origin_key, origin, channel_group
from {{ ref('lead_origin_group') }}
union all
select -1, 'n/a', 'Unknown'
