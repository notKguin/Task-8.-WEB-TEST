from __future__ import annotations

from django.conf import settings
from django.db import models

class TimeStampedModel(models.Model):
    """Абстрактная базовая модель: общие поля created_at/updated_at."""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True, verbose_name="Название")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self) -> str:
        return self.name


class Event(TimeStampedModel):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="events", verbose_name="Категория")
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    event_date = models.DateTimeField(verbose_name="Дата и время")
    location = models.CharField(max_length=200, verbose_name="Место")
    image = models.ImageField(upload_to="events/", blank=True, null=True, verbose_name="Изображение")

    class Meta:
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"
        ordering = ["-event_date"]

    def __str__(self) -> str:
        return self.title


class VolunteerApplication(TimeStampedModel):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        APPROVED = "approved", "Одобрена"
        REJECTED = "rejected", "Отклонена"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="volunteer_applications")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="applications")
    motivation = models.TextField(verbose_name="Комментарий / мотивация")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW, verbose_name="Статус")

    class Meta:
        verbose_name = "Заявка волонтёра"
        verbose_name_plural = "Заявки волонтёров"
        unique_together = ("user", "event")  # один пользователь — одна заявка на мероприятие

    def __str__(self) -> str:
        return f"{self.user} -> {self.event} ({self.status})"


class EventLike(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="event_likes")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="likes")

    class Meta:
        verbose_name = "Лайк"
        verbose_name_plural = "Лайки"
        unique_together = ("user", "event")

    def __str__(self) -> str:
        return f"{self.user} likes {self.event}"
