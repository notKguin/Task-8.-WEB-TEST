from __future__ import annotations

from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.models import Category, Event, VolunteerApplication, EventLike


class Command(BaseCommand):
    help = "Заполняет БД демо-данными (категории, мероприятия, пользователи, лайки, заявки)."

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        self.stdout.write(self.style.WARNING("Seeding demo data..."))

        # 1) Categories
        categories = [
            "Экология",
            "Социальная помощь",
            "Образование",
            "Культура и события",
            "Животные",
        ]
        category_map: dict[str, Category] = {}
        for name in categories:
            obj, _ = Category.objects.get_or_create(name=name)
            category_map[name] = obj

        # 2) Users (пароли хешируются Django автоматически)
        admin, admin_created = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@example.com", "is_staff": True, "is_superuser": True},
        )
        if admin_created:
            admin.set_password("admin12345")
            admin.save()

        user1, user1_created = User.objects.get_or_create(
            username="user1", defaults={"email": "user1@example.com"}
        )
        if user1_created:
            user1.set_password("user12345")
            user1.save()

        user2, user2_created = User.objects.get_or_create(
            username="user2", defaults={"email": "user2@example.com"}
        )
        if user2_created:
            user2.set_password("user12345")
            user2.save()

        # 3) Events
        now = timezone.now()

        event_data = [
            {
                "category": "Экология",
                "title": "Субботник в городском парке",
                "description": (
                    "Приглашаем волонтёров на субботник по уборке территории парка.\n\n"
                    "План работ: сбор мусора, очистка аллей и озеленённых зон. "
                    "Инвентарь выдаём на месте.\n\n"
                    "Продолжительность: около 3 часов."
                ),
                "event_date": now + timedelta(days=3, hours=1),
                "location": "Центральный городской парк",
            },
            {
                "category": "Социальная помощь",
                "title": "Помощь пожилым людям",
                "description": (
                    "Мероприятие направлено на поддержку пожилых людей и людей с ограниченной мобильностью.\n\n"
                    "Задачи: сопровождение, помощь с бытовыми задачами, общение и поддержка.\n\n"
                    "Перед началом проводится короткий инструктаж."
                ),
                "event_date": now + timedelta(days=5, hours=2),
                "location": "Центр социального обслуживания",
            },
            {
                "category": "Образование",
                "title": "Волонтёр-наставник для школьников",
                "description": (
                    "Нужны волонтёры для помощи школьникам: домашние задания, объяснение тем, мотивация.\n\n"
                    "Особенно приветствуются студенты и выпускники технических и гуманитарных направлений.\n\n"
                    "Занятия проходят в библиотеке в спокойной атмосфере."
                ),
                "event_date": now + timedelta(days=7, hours=3),
                "location": "Городская библиотека",
            },
            {
                "category": "Культура и события",
                "title": "Помощь в организации городского фестиваля",
                "description": (
                    "Требуются волонтёры на городской фестиваль.\n\n"
                    "Задачи: регистрация участников, навигация гостей, помощь организаторам, контроль порядка.\n\n"
                    "Волонтёрам предоставляются питание и благодарственные сертификаты."
                ),
                "event_date": now + timedelta(days=10, hours=4),
                "location": "Площадь у Дома культуры",
            },
            {
                "category": "Животные",
                "title": "Помощь приюту для животных",
                "description": (
                    "Помощь городскому приюту: кормление, уборка помещений, выгул собак.\n\n"
                    "Опыт не требуется — сотрудники проведут инструктаж.\n\n"
                    "Подойдёт всем, кто любит животных и готов помочь."
                ),
                "event_date": now + timedelta(days=12, hours=1),
                "location": "Городской приют для животных",
            },
        ]

        created_events: list[Event] = []
        for row in event_data:
            event, _ = Event.objects.get_or_create(
                title=row["title"],
                defaults={
                    "category": category_map[row["category"]],
                    "description": row["description"],
                    "event_date": row["event_date"],
                    "location": row["location"],
                },
            )
            created_events.append(event)

        # 4) Likes + Applications (демо)
        # Лайки
        for ev in created_events[:3]:
            EventLike.objects.get_or_create(user=user1, event=ev)

        for ev in created_events[1:4]:
            EventLike.objects.get_or_create(user=user2, event=ev)

        # Заявки
        VolunteerApplication.objects.get_or_create(
            user=user1,
            event=created_events[0],
            defaults={"motivation": "Хочу помочь городу и поработать в команде.", "status": VolunteerApplication.Status.NEW},
        )
        VolunteerApplication.objects.get_or_create(
            user=user2,
            event=created_events[1],
            defaults={"motivation": "Есть опыт волонтёрства, готов помогать людям.", "status": VolunteerApplication.Status.APPROVED},
        )

        self.stdout.write(self.style.SUCCESS("Done! Demo data created/updated."))
        self.stdout.write(self.style.WARNING("Demo users: admin/admin12345, user1/user12345, user2/user12345"))
