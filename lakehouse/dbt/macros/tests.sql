{# generic test: the combination of the given columns is unique (grain of a fact) #}
{% test unique_combination(model, columns) %}
select {{ columns | join(', ') }}, count(*) as n from {{ model }} group by {{ columns | join(', ') }} having count(*) > 1
{% endtest %}
