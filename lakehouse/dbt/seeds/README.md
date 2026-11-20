`dim_date_base.csv`: the calendar 2016-01-01 .. 2020-12-31 (1.827 rows) with Brazilian holidays (Python package `holidays`) and Black Friday, built by the
function `etl.build_dim_date.build_frame()` of the warehouse (no database needed): `python lakehouse/scripts/gen_dim_date_seed.py`.
The other reference seeds (state_region, category_group, ...) are the repository's own `seeds/` folder (see `seed-paths` in dbt_project.yml).
