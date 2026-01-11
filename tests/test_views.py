from __future__ import annotations

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from core.models import EventLike, VolunteerApplication
from .utils import create_event, create_user


class ViewsAccessAndCrudTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_password = "pass12345"
        cls.user = create_user(username="user", password=cls.user_password)
        cls.event = create_event(title="Тестовое мероприятие")

    def test_event_list_anonymous_200(self):
        resp = self.client.get(reverse("event_list"))
        self.assertEqual(resp.status_code, 200)

    def test_event_detail_anonymous_200(self):
        resp = self.client.get(reverse("event_detail", args=[self.event.pk]))
        self.assertEqual(resp.status_code, 200)

    def test_apply_requires_login(self):
        resp = self.client.get(reverse("apply_to_event", args=[self.event.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("login"), resp.url)

    def test_my_dashboard_requires_login(self):
        resp = self.client.get(reverse("my_dashboard"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("login"), resp.url)

    def test_apply_get_logged_in_200(self):
        self.client.login(username=self.user.username, password=self.user_password)
        resp = self.client.get(reverse("apply_to_event", args=[self.event.pk]))
        self.assertEqual(resp.status_code, 200)

    def test_apply_post_creates_application_and_redirects(self):
        self.client.login(username=self.user.username, password=self.user_password)

        before = VolunteerApplication.objects.count()
        resp = self.client.post(
            reverse("apply_to_event", args=[self.event.pk]),
            data={"motivation": "Хочу помочь"},
            follow=False,
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(VolunteerApplication.objects.count(), before + 1)

        app = VolunteerApplication.objects.get(user=self.user, event=self.event)
        self.assertEqual(app.motivation, "Хочу помочь")
        self.assertEqual(resp.url, reverse("event_detail", args=[self.event.pk]))

    def test_apply_duplicate_does_not_create_second(self):
        self.client.login(username=self.user.username, password=self.user_password)
        VolunteerApplication.objects.create(user=self.user, event=self.event, motivation="1")

        before = VolunteerApplication.objects.count()
        resp = self.client.post(reverse("apply_to_event", args=[self.event.pk]), data={"motivation": "2"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(VolunteerApplication.objects.count(), before)

    def test_toggle_like_requires_login(self):
        resp = self.client.post(reverse("toggle_like", args=[self.event.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("login"), resp.url)

    def test_toggle_like_adds_and_removes(self):
        self.client.login(username=self.user.username, password=self.user_password)

        resp1 = self.client.post(reverse("toggle_like", args=[self.event.pk]))
        self.assertEqual(resp1.status_code, 302)
        self.assertTrue(EventLike.objects.filter(user=self.user, event=self.event).exists())

        resp2 = self.client.post(reverse("toggle_like", args=[self.event.pk]))
        self.assertEqual(resp2.status_code, 302)
        self.assertFalse(EventLike.objects.filter(user=self.user, event=self.event).exists())

    def test_event_list_query_count_is_reasonable(self):
        # защита от N+1: список мероприятий должен грузиться малым числом запросов.
        # Правильная проверка: "не больше N", а не "ровно N".
        with CaptureQueriesContext(connection) as ctx:
            resp = self.client.get(reverse("event_list"))

        self.assertEqual(resp.status_code, 200)
        self.assertLessEqual(len(ctx.captured_queries), 5)
