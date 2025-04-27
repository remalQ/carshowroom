from django import template

register = template.Library()


@register.filter
def money_format(value):
    try:
        value = int(value)
        return f"{value:,}".replace(",", " ") + " руб."
    except (ValueError, TypeError):
        return value
