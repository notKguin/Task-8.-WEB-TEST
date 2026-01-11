from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from core.models import Category, Event, VolunteerApplication, EventLike
from .utils import create_category, create_event, create_user


class ModelCreationTests(TestCase):
    def test_create_category(self):
        obj = create_category("Экология")
        self.assertIsInstance(obj, Category)
        self.assertIsNotNone(obj.pk)

    def test_create_event_with_fk(self):
        cat = create_category("Образование")
        event = create_event(category=cat, title="Мастер-класс")
        self.assertEqual(event.category, cat)
        self.assertIsNotNone(event.pk)

    def test_create_volunteer_application_and_relations(self):
        user = create_user(username="u1")
        event = create_event(title="Субботник")
        app = VolunteerApplication.objects.create(user=user, event=event, motivation="Хочу помочь")
        self.assertEqual(app.user, user)
        self.assertEqual(app.event, event)

        # обратные связи
        self.assertIn(event, [a.event for a in user.volunteer_applications.all()])
        self.assertIn(app, list(event.applications.all()))

    def test_create_like_and_relations(self):
        user = create_user(username="u2")
        event = create_event(title="Сбор средств")
        like = EventLike.objects.create(user=user, event=event)

        self.assertEqual(like.user, user)
        self.assertEqual(like.event, event)
        self.assertIn(like, list(user.event_likes.all()))
        self.assertIn(like, list(event.likes.all()))

    def test_timestamps_are_filled(self):
        cat = create_category("Культура")
        self.assertIsNotNone(cat.created_at)
        self.assertIsNotNone(cat.updated_at)

        before = cat.updated_at
        cat.name = "Культура и искусство"
        cat.save()
        cat.refresh_from_db()

        self.assertGreaterEqual(cat.updated_at, before)
        # created_at не должен меняться
        self.assertLessEqual(cat.created_at, cat.updated_at)

    def test_unique_constraints(self):
        create_category("Спорт")
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="Спорт")

    def test_unique_together_application(self):
        user = create_user(username="u3")
        event = create_event(title="Конференция")
        VolunteerApplication.objects.create(user=user, event=event, motivation="1")

        with self.assertRaises(IntegrityError):
            VolunteerApplication.objects.create(user=user, event=event, motivation="2")

    def test_unique_together_like(self):
        user = create_user(username="u4")
        event = create_event(title="Ярмарка")
        EventLike.objects.create(user=user, event=event)

        with self.assertRaises(IntegrityError):
            EventLike.objects.create(user=user, event=event)
