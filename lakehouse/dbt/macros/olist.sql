{# yyyymmdd key of a timestamp; -1 (Unknown member) when NULL or outside dim_date (2016-01-01 .. 2020-12-31): dw.date_key of the warehouse #}
{% macro date_key(ts) -%}
    (case when {{ ts }} is null or cast({{ ts }} as date) not between date '2016-01-01' and date '2020-12-31' then -1
          else cast(date_format({{ ts }}, '%Y%m%d') as integer) end)
{%- endmacro %}

{# timestamp WITHOUT time zone from the UTC timestamptz that Spark writes (the warehouse columns are 'timestamp') #}
{% macro ts(col) -%}cast({{ col }} as timestamp(6)){%- endmacro %}

{# round(seconds / divisor, 2) in integer arithmetic, half away from zero like PostgreSQL numeric (a double would round 0.015 down). seconds >= 0 only #}
{% macro round2(seconds, divisor) -%}
    (cast((200 * ({{ seconds }}) + {{ divisor }}) / (2 * {{ divisor }}) as decimal(18, 0)) * 0.01)
{%- endmacro %}

{# seconds between two timestamps (b - a) #}
{% macro secs(a, b) -%}date_diff('second', {{ a }}, {{ b }}){%- endmacro %}
