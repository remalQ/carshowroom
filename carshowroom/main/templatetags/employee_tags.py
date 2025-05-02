from django import template

register = template.Library()


@register.filter(name='is_employee')
def is_employee(user):
    return user.groups.filter(name='Менеджеры').exists()
