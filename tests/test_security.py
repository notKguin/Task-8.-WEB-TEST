from __future__ import annotations

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import authenticate

from core.models import Category
from .utils import create_user


class SecurityTests(TestCase):
    def test_password_is_hashed(self):
        user = create_user(username="hashme", password="PlainPass12345")
        self.assertNotEqual(user.password, "PlainPass12345")
        # стандартные hasher'ы Django обычно начинаются с algo$
        self.assertIn("$", user.password)

    def test_sql_injection_like_login_does_not_work(self):
        # Попытка «SQL-инъекции» через поле username должна просто не пройти аутентификацию.
        user = create_user(username="realuser", password="RealPass12345")
        bad_username = "' OR 1=1 --"
        authed = authenticate(username=bad_username, password="anything")
        self.assertIsNone(authed)

        resp = self.client.post(reverse("login"), data={"username": bad_username, "password": "anything"})
        # страница логина возвращает 200 с ошибкой формы
        self.assertEqual(resp.status_code, 200)

    def test_xss_is_escaped_in_templates(self):
        payload = '<script>alert("xss")</script>'
        Category.objects.create(name=payload)

        resp = self.client.get(reverse("event_list"))
        self.assertEqual(resp.status_code, 200)

        # В шаблонах Django автоэкранирование включено по умолчанию.
        self.assertIn("&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;", resp.content.decode("utf-8"))
        self.assertNotIn(payload, resp.content.decode("utf-8"))
