from __future__ import annotations

from django.contrib.auth import authenticate
from django.test import TestCase
from django.urls import reverse

from core.models import Category, Event
from .utils import create_user


class SecurityTests(TestCase):
    def test_password_is_hashed(self):
        user = create_user(username="hashme", password="PlainPass12345")
        self.assertNotEqual(user.password, "PlainPass12345")
        # стандартные hasher'ы Django обычно начинаются с algo$
        self.assertIn("$", user.password)

    def test_sql_injection_like_login_does_not_work(self):
        # Попытка «SQL-инъекции» через поле username должна просто не пройти аутентификацию.
        create_user(username="realuser", password="RealPass12345")
        bad_username = "' OR 1=1 --"

        authed = authenticate(username=bad_username, password="anything")
        self.assertIsNone(authed)

        resp = self.client.post(reverse("login"), data={"username": bad_username, "password": "anything"})
        # страница логина возвращает 200 с ошибкой формы
        self.assertEqual(resp.status_code, 200)

    def test_xss_is_escaped_in_templates(self):
        payload = '<script>alert("xss")</script>'

        category = Category.objects.create(name="Cat XSS")
        Event.objects.create(
            category=category,
            title=payload,
            description="desc",
            event_date="2030-01-01",
            location="loc",
        )

        resp = self.client.get(reverse("event_list"))
        self.assertEqual(resp.status_code, 200)

        html = resp.content.decode("utf-8")

        # Сырой скрипт не должен попасть в HTML (не должно быть "живого" тега)
        self.assertNotIn(payload, html)

        # Экранированный должен быть виден
        self.assertIn("&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;", html)
