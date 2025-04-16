# billing/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def cents_to_ghs(value):
    try:
        # Ensure the value is treated as a number (float or int)
        value = float(value)
        return value / 100 if value is not None else 0
    except (ValueError, TypeError):
        # Return 0 if the value cannot be converted to a number
        return 0


# custom_filters.py
from django import template

register = template.Library()

@register.filter(name='absolute_value')
def absolute_value(value):
    try:
        return abs(value)
    except (TypeError, ValueError):
        return value