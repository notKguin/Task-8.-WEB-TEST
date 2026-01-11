from __future__ import annotations

from django.test import TestCase

from core.forms import AdminExportForm, SignUpForm, VolunteerApplicationForm
from core.models import VolunteerApplication
from .utils import create_user, create_event


class FormsTests(TestCase):
    def test_signup_form_valid(self):
        form = SignUpForm(
            data={
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "StrongPass12345",
                "password2": "StrongPass12345",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertTrue(user.pk)
        self.assertEqual(user.email, "newuser@example.com")
        self.assertNotEqual(user.password, "StrongPass12345")  # хеш

    def test_signup_form_invalid_password_mismatch(self):
        form = SignUpForm(
            data={
                "username": "newuser2",
                "email": "newuser2@example.com",
                "password1": "StrongPass12345",
                "password2": "StrongPass123456",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_signup_form_invalid_missing_email(self):
        form = SignUpForm(
            data={
                "username": "newuser3",
                "password1": "StrongPass12345",
                "password2": "StrongPass12345",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_application_form_valid(self):
        form = VolunteerApplicationForm(data={"motivation": "Готов помогать"})
        self.assertTrue(form.is_valid(), form.errors)
        obj = form.save(commit=False)
        self.assertIsInstance(obj, VolunteerApplication)

    def test_application_form_invalid_empty(self):
        form = VolunteerApplicationForm(data={"motivation": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("motivation", form.errors)

    def test_admin_export_form_validation(self):
        form = AdminExportForm(data={"models": ["core.Category"]})
        # choices пустые в форме по умолчанию; имитируем заполнение как в admin view
        form.fields["models"].choices = [("core.Category", "core.Category")]
        self.assertTrue(form.is_valid(), form.errors)

        form2 = AdminExportForm(data={"models": []})
        form2.fields["models"].choices = [("core.Category", "core.Category")]
        self.assertFalse(form2.is_valid())
        self.assertIn("models", form2.errors)
