from __future__ import annotations

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import VolunteerApplication


class SignUpForm(UserCreationForm):
    """Регистрация пользователя (используем стандартную модель User)."""
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class VolunteerApplicationForm(forms.ModelForm):
    class Meta:
        model = VolunteerApplication
        fields = ("motivation",)
        widgets = {
            "motivation": forms.Textarea(attrs={"rows": 4, "placeholder": "Почему вы хотите стать волонтёром?"}),
        }


class AdminExportForm(forms.Form):
    """Форма экспорта: выбрать таблицы (модели). Поля берутся как в админке (list_display)."""
    models = forms.MultipleChoiceField(
        label="Таблицы (модели)",
        required=True,
        widget=forms.CheckboxSelectMultiple,
        choices=[],
    )
