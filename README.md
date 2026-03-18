# Telegram Shop Bot

Трехсервисный интернет-магазин: Telegram-бот (Aiogram 3), админ-панель (Django), WebApp (React/TS).

## Архитектура
- **Общая БД**: PostgreSQL хранит каталог, корзины, заказы, пользователей.
- **Telegram-бот**: асинхронный SQLAlchemy, каталог, корзина, заказы, FSM, inline-FAQ.
- **Django Admin + API**: CRUD, экспорт заказов, REST API для WebApp.
- **WebApp**: React-приложение внутри Telegram, работает через API и initData.
- **Уведомления**: Django отправляет HTTP-уведомления в бота (новый заказ, смена статуса, рассылки).

## Запуск
1. Скопируйте `.env.example` в `.env` и заполните значения.
2. Запуск: `docker-compose up --build`.
3. Admin: `http://localhost:8000/admin`
4. WebApp: `http://localhost:5173`

## Переменные окружения
- `BOT_TOKEN` — токен Telegram-бота.
- `DJANGO_SECRET_KEY` — секрет Django.
- `DB_*` — параметры PostgreSQL.
- `BOT_INTERNAL_TOKEN` — токен для внутренних уведомлений.
- `ADMIN_CHAT_ID` — чат для админ-уведомлений.
- `ADMIN_IDS` — список Telegram ID админов (через запятую).
- `WEBAPP_URL` — ссылка на WebApp для кнопки в боте.
- `MEDIA_BASE_URL` — базовый URL для медиа (например `http://localhost:8000/media`).
- `CORS_ALLOWED_ORIGINS` / `CSRF_TRUSTED_ORIGINS` — домены WebApp.
- `VITE_TEST_TELEGRAM_ID` — тестовый Telegram ID для локальной отладки WebApp.

## Структура проекта
- `bot/` — Telegram-бот (Aiogram).
- `admin/` — Django-проект и REST API.
- `webapp/` — React WebApp.
- `docker-compose.yml` — оркестрация сервисов.

## Примеры API
- `GET /api/v1/categories/`
- `GET /api/v1/products/?category=<id>`
- `GET /api/v1/cart/`
- `POST /api/v1/cart/add_item/`
- `POST /api/v1/cart/update_item/`
- `POST /api/v1/orders/`
