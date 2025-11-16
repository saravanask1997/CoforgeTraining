from django import template

register = template.Library()

@register.filter
def get_option(q, number):
    field = f"option_{number}"
    return getattr(q, field, None)