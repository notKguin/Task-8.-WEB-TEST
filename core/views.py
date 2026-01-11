from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import SignUpForm, VolunteerApplicationForm
from .models import Event, VolunteerApplication, EventLike


def event_list(request: HttpRequest) -> HttpResponse:
    # Гость может смотреть список
    events = (
        Event.objects
        .select_related("category")
        .annotate(
            likes_count=Count("likes", distinct=True),
            applications_count=Count("applications", distinct=True),
        )
        .order_by("-event_date")
    )
    return render(request, "events/event_list.html", {"events": events})


def event_detail(request: HttpRequest, pk: int) -> HttpResponse:
    event = (
        Event.objects
        .select_related("category")
        .annotate(
            likes_count=Count("likes", distinct=True),
            applications_count=Count("applications", distinct=True),
        )
        .filter(pk=pk)
        .first()
    )
    if not event:
        event = get_object_or_404(Event, pk=pk)

    liked = False
    application = None
    if request.user.is_authenticated:
        liked = EventLike.objects.filter(user=request.user, event=event).exists()
        application = VolunteerApplication.objects.filter(user=request.user, event=event).first()

    form = VolunteerApplicationForm()
    return render(
        request,
        "events/event_detail.html",
        {
            "event": event,
            "liked": liked,
            "application": application,
            "form": form,
        },
    )


@login_required
def apply_to_event(request: HttpRequest, pk: int) -> HttpResponse:
    event = get_object_or_404(Event, pk=pk)

    # Если заявка уже есть — не создаём повторно
    existing = VolunteerApplication.objects.filter(user=request.user, event=event).first()
    if existing:
        messages.info(request, "Вы уже подали заявку на это мероприятие.")
        return redirect("event_detail", pk=event.pk)

    if request.method == "POST":
        form = VolunteerApplicationForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.event = event
            obj.save()
            messages.success(request, "Заявка отправлена! Ожидайте решения организатора.")
            return redirect("event_detail", pk=event.pk)
    else:
        form = VolunteerApplicationForm()

    return render(request, "events/apply.html", {"event": event, "form": form})


@login_required
@require_POST
def toggle_like(request: HttpRequest, pk: int) -> HttpResponse:
    event = get_object_or_404(Event, pk=pk)
    like = EventLike.objects.filter(user=request.user, event=event).first()
    if like:
        like.delete()
        messages.info(request, "Лайк убран.")
    else:
        EventLike.objects.create(user=request.user, event=event)
        messages.success(request, "Спасибо за поддержку! Лайк добавлен.")
    return redirect("event_detail", pk=event.pk)


def signup(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("event_list")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация успешна. Добро пожаловать!")
            return redirect("event_list")
    else:
        form = SignUpForm()

    return render(request, "auth/signup.html", {"form": form})


@login_required
def my_dashboard(request: HttpRequest) -> HttpResponse:
    applications = (
        VolunteerApplication.objects
        .select_related("event", "event__category")
        .filter(user=request.user)
        .order_by("-created_at")
    )
    likes = EventLike.objects.select_related("event").filter(user=request.user).order_by("-created_at")
    return render(request, "profile/dashboard.html", {"applications": applications, "likes": likes})
