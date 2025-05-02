from django import template
from ..models import Employee

register = template.Library()


@register.filter
def has_salesemployee(user):
    return Employee.objects.filter(user=user).exists()
