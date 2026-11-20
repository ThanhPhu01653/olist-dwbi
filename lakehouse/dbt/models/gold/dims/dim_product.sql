select cast(row_number() over (order by p.product_id) as integer) as product_key,
       p.product_id, p.product_category_name as category_name_pt,
       coalesce(t.product_category_name_english, x.product_category_name_english, p.product_category_name) as category_name_en,
       coalesce(gr.category_group, 'Unknown') as category_group,
       p.weight_g, p.length_cm, p.height_cm, p.width_cm,
       cast(p.length_cm as bigint) * p.height_cm * p.width_cm as volume_cm3,
       case when p.weight_g is null or p.weight_g = 0 then 'Unknown' when p.weight_g < 500 then 'S' when p.weight_g < 2000 then 'M'
            when p.weight_g < 10000 then 'L' else 'XL' end as size_class,
       p.photos_qty, p.name_length, p.description_length
from {{ source('silver', 'products') }} p
left join {{ source('silver', 'category_translation') }} t on t.product_category_name = p.product_category_name
left join {{ ref('category_translation_extra') }} x on x.product_category_name = p.product_category_name
left join {{ ref('category_group') }} gr on gr.product_category_name = p.product_category_name
union all
select -1, 'unknown', 'unknown', 'unknown', 'Unknown', null, null, null, null, null, 'Unknown', null, null, null
