from django import template

register = template.Library()

@register.filter
def zfill(value, width):
    return str(value).zfill(width)
