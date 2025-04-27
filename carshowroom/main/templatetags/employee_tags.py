from django import template
from ..models import SalesEmployee

register = template.Library()


@register.filter
def has_salesemployee(user):
    return SalesEmployee.objects.filter(user=user).exists()

