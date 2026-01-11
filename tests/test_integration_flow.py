from __future__ import annotations

from django.test import TestCase
from django.urls import reverse

from core.models import VolunteerApplication, EventLike
from .utils import create_event, create_user


class IntegrationFlowTests(TestCase):
    def test_full_user_flow_apply_like_and_dashboard(self):
        password = "pass12345"
        user = create_user(username="flowuser", password=password)
        event = create_event(title="Интеграционное")

        # 1) логин
        self.assertTrue(self.client.login(username=user.username, password=password))

        # 2) лайк
        self.client.post(reverse("toggle_like", args=[event.pk]))
        self.assertTrue(EventLike.objects.filter(user=user, event=event).exists())

        # 3) подача заявки
        before = VolunteerApplication.objects.count()
        resp = self.client.post(reverse("apply_to_event", args=[event.pk]), data={"motivation": "Хочу!"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(VolunteerApplication.objects.count(), before + 1)

        # 4) личный кабинет отражает данные
        resp2 = self.client.get(reverse("my_dashboard"))
        self.assertEqual(resp2.status_code, 200)
        html = resp2.content.decode("utf-8")
        self.assertIn("Интеграционное", html)
