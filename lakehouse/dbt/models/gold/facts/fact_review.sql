-- depends_on: {{ ref('dim_date') }}
{# transaction fact, grain = (review, order); delivered_late comes from fact_order_fulfillment.
   'Has a comment' = something left after removing SPACES at both ends, as PostgreSQL trim() does; Trino trim() also removes line breaks and tabs, which
   made 18 reviews that contain only a line break count as 'no comment' (found by reconcile.py). #}
select r.review_id, r.order_id,
       {{ date_key(ts('r.review_creation_date')) }} as review_creation_date_key, {{ date_key(ts('r.review_answer_timestamp')) }} as review_answer_date_key,
       coalesce(dc.customer_key, -1) as customer_key, cast(r.review_score as integer) as review_score,
       cast(r.review_score <= 2 as integer) as is_negative,
       cast(nullif(regexp_replace(r.review_comment_title, '^ +| +$', ''), '') is not null as integer) as has_comment_title,
       cast(nullif(regexp_replace(r.review_comment_message, '^ +| +$', ''), '') is not null as integer) as has_comment_message,
       coalesce(length(nullif(regexp_replace(r.review_comment_message, '^ +| +$', ''), '')), 0) as comment_length,
       case when {{ secs(ts('r.review_creation_date'), ts('r.review_answer_timestamp')) }} >= 0
            then {{ round2(secs(ts('r.review_creation_date'), ts('r.review_answer_timestamp')), 3600) }} end as response_hours,
       coalesce(f.is_late, 0) as delivered_late, coalesce(f.is_delivered, 0) as is_delivered
from {{ source('silver', 'order_reviews') }} r
join {{ source('silver', 'orders') }} o on o.order_id = r.order_id
join {{ source('silver', 'customers') }} c on c.customer_id = o.customer_id
left join {{ ref('dim_customer') }} dc on dc.customer_unique_id = c.customer_unique_id
     and cast(o.order_purchase_timestamp as date) between dc.effective_from and dc.effective_to
left join {{ ref('fact_order_fulfillment') }} f on f.order_id = r.order_id
