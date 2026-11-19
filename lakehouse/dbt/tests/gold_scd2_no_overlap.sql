-- custom test: SCD2 versions of one customer never overlap in time
select a.customer_unique_id, a.effective_from, a.effective_to, b.effective_from as next_from
from {{ ref('dim_customer') }} a join {{ ref('dim_customer') }} b
  on a.customer_unique_id = b.customer_unique_id and a.version_no + 1 = b.version_no
where a.customer_key <> -1 and a.effective_to >= b.effective_from
