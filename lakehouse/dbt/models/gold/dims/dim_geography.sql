{# zips of geolocation, customers and sellers (like dw.load_dim_geography) enriched with the IBGE municipality, microregion, mesoregion and population (P9) #}
with cs as (
    select zip, city, st, count(*) as n from (
        select zip_code_prefix as zip, city, state_code as st from {{ source('silver', 'customers') }}
        union all select zip_code_prefix, city, state_code from {{ source('silver', 'sellers') }}) u
    where zip is not null group by zip, city, st
),
city_mode as (
    select zip, city from (select zip, city, row_number() over (partition by zip order by n desc, city) as r
                           from (select zip, city, sum(n) as n from cs where city is not null group by zip, city)) where r = 1
),
st_mode as (
    select zip, st from (select zip, st, row_number() over (partition by zip order by n desc, st) as r
                         from (select zip, st, sum(n) as n from cs where st is not null group by zip, st)) where r = 1
),
other as (select z.zip, c.city, s.st from (select distinct zip from cs) z left join city_mode c on c.zip = z.zip left join st_mode s on s.zip = z.zip),
z as (
    select coalesce(g.zip_code_prefix, o.zip) as zip, coalesce(g.city, o.city) as city, coalesce(g.state_code, o.st) as st, g.latitude, g.longitude
    from {{ source('silver', 'geolocation_zip') }} g full join other o on o.zip = g.zip_code_prefix
),
x as (
    select z.*, r.state_name, r.region, m.ibge_code, i.microrregiao, i.mesorregiao, p16.population as p16, p17.population as p17, p18.population as p18,
           coalesce(m.method, 'unmatched') as match_method
    from z
    left join {{ ref('state_region') }} r on r.state_code = z.st
    left join {{ source('silver', 'city_ibge_match') }} m on m.state_code = z.st and m.city = z.city
    left join {{ source('silver', 'ibge_municipio') }} i on i.ibge_code = m.ibge_code
    left join {{ source('silver', 'ibge_population') }} p16 on p16.ibge_code = m.ibge_code and p16.year = 2016
    left join {{ source('silver', 'ibge_population') }} p17 on p17.ibge_code = m.ibge_code and p17.year = 2017
    left join {{ source('silver', 'ibge_population') }} p18 on p18.ibge_code = m.ibge_code and p18.year = 2018
)
select cast(row_number() over (order by zip) as integer) as geography_key, zip as zip_code_prefix, city, st as state_code,
       coalesce(state_name, 'Unknown') as state_name, coalesce(region, 'Unknown') as region, 'Brazil' as country, latitude, longitude,
       cast(ibge_code as integer) as ibge_municipio_code, microrregiao, mesorregiao,
       cast(p16 as integer) as populacao_2016, cast(p17 as integer) as populacao_2017, cast(p18 as integer) as populacao_2018, match_method
from x
union all
select -1, null, 'unknown', null, 'Unknown', 'Unknown', 'Brazil', null, null, null, null, null, null, null, null, null
