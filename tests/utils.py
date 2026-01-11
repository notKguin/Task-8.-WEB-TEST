from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import Category, Event


def create_user(*, username: str = "user", password: str = "pass12345", is_staff: bool = False, is_superuser: bool = False):
    User = get_user_model()
    return User.objects.create_user(
        username=username,
        password=password,
        is_staff=is_staff,
        is_superuser=is_superuser,
    )


def create_category(name: str = "Помощь животным") -> Category:
    return Category.objects.create(name=name)


def create_event(*, category: Category | None = None, title: str = "Сбор вещей", days_from_now: int = 3) -> Event:
    if category is None:
        category = create_category()
    return Event.objects.create(
        category=category,
        title=title,
        description="Описание мероприятия",
        event_date=timezone.now() + timedelta(days=days_from_now),
        location="Амстердам",
    )
