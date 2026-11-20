with r as (
    select sdr_id as rep_id, 'SDR' as rep_role from {{ source('silver', 'closed_deals') }} where sdr_id is not null
    union
    select sr_id, 'SR' from {{ source('silver', 'closed_deals') }} where sr_id is not null
)
select cast(row_number() over (order by rep_role, rep_id) as integer) as sales_rep_key, rep_id, rep_role from r
union all
select -1, 'n/a', 'n/a'
