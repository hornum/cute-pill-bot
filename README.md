# 💊 Cute Pill Bot

Telegram-бот для напоминаний о приёме лекарств. Позволяет добавлять таблетки с расписанием и получать ежедневные напоминания в заданное время.

Проект создан для обучения и личного использования. Он поднят прямо сейчас, опробовать бота можно по ссылке https://t.me/CutePillBot

## Возможности

- Добавление таблеток с названием, дозировкой и временем приёма
- Ежедневные напоминания в заданное время
- Подтверждение приёма, пропуск или откладывание напоминания на 15 минут
- Просмотр списка таблеток с возможностью управления каждой
- Редактирование названия, дозировки и времени приёма
- Удаление таблеток
- Ограничение до 10 таблеток на пользователя

## Стек

- **Python 3.12**
- **aiogram 3**
- **APScheduler**
- **SQLAlchemy 2 (async)** + **asyncpg**
- **Alembic**
- **PostgreSQL 16**
- **Docker + Docker Compose**

## Структура проекта

```
cute-pill-bot/
├── app/
│   ├── bot/
│   │   ├── handlers/
│   │   │   ├── __init__.py
│   │   │   ├── medicines.py        # добавление и вывод списка таблеток
│   │   │   ├── medicines_edit.py   # коллбеки изменения таблетки
│   │   │   ├── medicines_delete.py # коллбеки удаления таблетки
│   │   │   ├── reminders.py        # коллбеки напоминаний
│   │   │   └── start.py            # /start, /help
│   │   ├── instance.py             # экземпляры bot и scheduler
│   │   ├── keyboards.py            # клавиатуры
│   │   └── states.py               # FSM состояния
│   ├── db/     
│   │   ├── base.py                 # базовый класс модели
│   │   ├── models.py               # модели
│   │   └── session.py              # фабрика сессий
│   ├── scheduler/      
│   │   └── jobs.py                 # задачи планировщика
│   ├── service/        
│   │   ├── pill_service.py         # логика работы с таблетками
│   │   ├── reminder_service.py     # логика работы с напоминаниями
│   │   └── user_service.py         # логика работы с пользователями
│   ├── config.py
│   └── main.py
├── migrations/
├── .env.example
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Установка и запуск

### Локально

1. Клонируй репозиторий:
```bash
git clone https://github.com/hornum/cute-pill-bot.git
cd cute-pill-bot
```

2. Создай `.env` файл на основе `.env.example`:
```bash
cp .env.example .env
```

3. Заполни `.env`:
```
DB_USER=postgres
DB_PASS=пароль
DB_HOST=db
DB_PORT=5432
DB_NAME=cute-pill-bot
TOKEN=тг-токен
```

4. Запусти через Docker Compose:
```bash
docker-compose up -d --build
```

5. Примени миграции:
```bash
docker-compose exec app alembic upgrade head
```

### На сервере

Те же шаги — Docker должен быть установлен на сервере. Подключись по SSH и повтори шаги выше.

## Команды бота

| Команда | Описание              |
|---------|-----------------------|
| `/start` | Начать работу с ботом |
| `/help` | Список команд         |
| `/add` | Добавить таблетку     |
| `/list` | Список таблеток       |
