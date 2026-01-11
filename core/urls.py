from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("", views.event_list, name="event_list"),
    path("events/<int:pk>/", views.event_detail, name="event_detail"),
    path("events/<int:pk>/apply/", views.apply_to_event, name="apply_to_event"),
    path("events/<int:pk>/like/", views.toggle_like, name="toggle_like"),

    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="auth/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("my/", views.my_dashboard, name="my_dashboard"),
]
