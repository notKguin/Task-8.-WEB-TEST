from django import template

register = template.Library()

@register.filter
def has_group(user, group_name: str) -> bool:
    """Пример расширения прав (не обязателен): проверка группы."""
    return user.is_authenticated and user.groups.filter(name=group_name).exists()
