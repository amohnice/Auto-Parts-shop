from django import template

register = template.Library()

@register.filter
def range_filter(value, max_value):
    return range(1, max_value)
