# Volunteer Service (Django + PostgreSQL + Docker)

Веб‑приложение: **заявки на участие в мероприятиях в роли волонтёра** + **лайки**.
Реализовано:
- PostgreSQL (минимум 3 связанных таблицы: `Category`, `Event`, `VolunteerApplication`, `EventLike`)
- Абстрактная базовая модель с `created_at`, `updated_at`
- Роли: Гость (без авторизации), Зарегистрированный пользователь, Администратор (Django admin)
- Основной сервис: подача заявки на мероприятие
- Доп. функционал: лайк мероприятия
- Админка: экспорт данных в **XLSX** с выбором **таблиц** и **полей**
- Docker / docker-compose
- Static + Media (изображения), отображаются корректно
- Безопасность: ORM (SQLi), autoescape шаблонов (XSS), CSRF protection (POST)

## Быстрый старт (Docker)

1) Скопируйте `.env.example` в `.env` и при необходимости измените значения:
```bash
cp .env.example .env
```

2) Сборка и запуск:
```bash
docker compose up --build
```

3) Миграции и суперпользователь (в другом терминале):
```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

4) Открыть:
- Приложение: http://localhost:8000/
- Админка: http://localhost:8000/admin/

## Демо‑данные
После запуска зайдите в админку и создайте:
- Category
- Event (можно добавить изображение)
Затем пользователи смогут лайкать и подавать заявки.

## Важно
- Пароли хранятся в зашифрованном виде штатными механизмами Django (`pbkdf2` по умолчанию).
- Для production замените `DEBUG=0`, задайте `SECRET_KEY`, настройте `ALLOWED_HOSTS`.
