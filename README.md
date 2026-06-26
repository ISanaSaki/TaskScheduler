# 📅 Task Scheduler

![FastAPI](https://img.shields.io/badge/FastAPI-0.136.3-009688?style=flat&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python)
![Celery](https://img.shields.io/badge/Celery-5.6.3-37814A?style=flat&logo=celery)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat&logo=redis)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=flat&logo=postgresql)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat)

A production-ready background task scheduling system with real-time status tracking and email notifications.

---

## ✨ Features

- 🔐 **JWT Authentication** — register, login, refresh token
- 📧 **Real Email Sending** — via SMTP (Gmail and others)
- 🔁 **Recurring Tasks** — cron expression support with APScheduler
- ⚡ **Async Task Execution** — Celery + Redis
- 📡 **Real-time Status** — WebSocket with JWT auth
- 🗄️ **PostgreSQL** — SQLModel + Alembic migrations
- 📝 **Logging** — file + console with rotation
- 🛡️ **Rate Limiting** — per IP and per user
- 🐳 **Docker** — PostgreSQL and Redis via Docker Compose

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Task Queue | Celery |
| Message Broker & Backend | Redis |
| Scheduler | APScheduler 3.x |
| ORM | SQLModel + SQLAlchemy |
| Migrations | Alembic |
| Database | PostgreSQL |
| Auth | JWT (python-jose) + Argon2 |
| Email | aiosmtplib |
| Rate Limiting | SlowAPI |

---

## 📁 Project Structure

```
TaskScheduler/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py        # Register, login, refresh
│   │       ├── tasks.py       # Task CRUD endpoints
│   │       └── ws.py          # WebSocket real-time status
│   ├── core/
│   │   ├── config.py          # Settings from .env
│   │   ├── database.py        # Async DB engine & session
│   │   ├── email.py           # SMTP email service
│   │   ├── limiter.py         # Rate limiter setup
│   │   ├── logger.py          # Logging configuration
│   │   ├── scheduler.py       # APScheduler setup
│   │   └── security.py        # JWT & password hashing
│   ├── models/
│   │   ├── task.py            # Task & TaskRun models
│   │   └── user.py            # User model
│   ├── schemas/
│   │   ├── auth.py            # Auth schemas
│   │   └── task.py            # Task schemas
│   ├── worker/
│   │   ├── celery_app.py      # Celery configuration
│   │   └── tasks.py           # Celery task definitions
│   └── main.py
├── alembic/                   # DB migrations
├── logs/                      # Log files (auto-created)
├── .env.example
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## ⚙️ Setup & Run

### Prerequisites
- Python 3.12
- Docker & Docker Compose

### 1. Clone & configure

```bash
git clone https://github.com/ISanaSaki/TaskScheduler.git
cd TaskScheduler
cp .env.example .env
# Edit .env with your values
```

### 2. Start PostgreSQL & Redis

```bash
docker compose up -d
```

### 3. Install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
alembic upgrade head
```

### 5. Start Celery worker

```bash
celery -A app.worker.celery_app.celery_app worker --loglevel=info --pool=solo
```

### 6. Start API server

```bash
uvicorn app.main:app --reload
```

Visit **http://localhost:8000/docs** for the interactive API documentation.

---

## 📡 API Endpoints

### Auth

| Method | Endpoint | Rate Limit | Description |
|---|---|---|---|
| POST | `/auth/register` | 5/min | Register a new user |
| POST | `/auth/login` | 10/min | Login and get tokens |
| POST | `/auth/refresh` | 20/min | Refresh access token |

### Tasks

| Method | Endpoint | Rate Limit | Description |
|---|---|---|---|
| POST | `/tasks/` | 30/min | Create a new task (max 10 per user) |
| GET | `/tasks/` | — | List your tasks |
| GET | `/tasks/{id}/runs` | — | Get task run history |
| DELETE | `/tasks/{id}` | — | Delete a task |

### WebSocket

| Endpoint | Auth | Description |
|---|---|---|
| `ws://host/ws/tasks/{id}?token=<jwt>` | Query JWT | Real-time task status |

---

## 🔐 Auth Flow

### Register
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com", "password": "secret"}'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=secret"
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

- **access_token** — valid for 30 minutes, used for all API requests
- **refresh_token** — valid for 7 days, used to get a new access token

### Refresh Token
```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "eyJ..."}'
```

---

## 📧 Task Examples

### One-off Email Task
```json
{
  "name": "Welcome Email",
  "is_recurring": false,
  "email_to": "user@example.com",
  "email_subject": "Welcome!",
  "email_body": "Thanks for signing up."
}
```
Runs immediately via Celery.

### Recurring Task (Cron)
```json
{
  "name": "Weekly Report",
  "is_recurring": true,
  "cron_expression": "0 9 * * 1",
  "email_to": "boss@example.com",
  "email_subject": "Weekly Report",
  "email_body": "Here is your weekly report."
}
```
Runs every Monday at 9:00 AM via APScheduler.

---

## 📡 WebSocket Usage

Connect with your JWT token as a query parameter:

```
ws://localhost:8000/ws/tasks/{task_id}?token=<access_token>
```

Messages:
```json
{ "task_id": 1, "status": "running", "result": null }
{ "task_id": 1, "status": "done", "result": "Email sent to user@example.com" }
```

Connection closes automatically when task reaches `done` or `failed`.

Use `test_ws.html` in the repo root for a quick browser test.

---

## 📝 Logging

Logs are written to both console and `logs/app.log`:

```
2026-06-25 14:08:58 | INFO  | auth   | User 'alice' logged in successfully
2026-06-25 14:09:20 | INFO  | tasks  | Task 5 created and dispatched to Celery - user: 'alice'
2026-06-25 14:09:25 | INFO  | worker | Task 5 started - sending email to 'bob@example.com'
2026-06-25 14:09:28 | INFO  | worker | Task 5 completed - Email sent to 'bob@example.com'
```

Log files rotate at 5MB, keeping 3 backups.

---

## 🛡️ Rate Limiting

| Endpoint | Limit |
|---|---|
| POST `/auth/register` | 5 requests/minute |
| POST `/auth/login` | 10 requests/minute |
| POST `/auth/refresh` | 20 requests/minute |
| POST `/tasks/` | 30 requests/minute |
| Max tasks per user | 10 tasks |

Exceeding limits returns `429 Too Many Requests`.

---

## 🔧 Environment Variables

```env
DATABASE_URL=postgresql+asyncpg://postgres:PASSWORD@localhost:5434/scheduler_db
CELERY_BROKER_URL=redis://localhost:6380/0
CELERY_RESULT_BACKEND=redis://localhost:6380/0
POSTGRES_PASSWORD=YOUR_PASSWORD
SECRET_KEY=your-secret-key
ALGORITHM=HS256
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=Task Scheduler
```

> For Gmail, use an **App Password** from Google Account → Security → 2-Step Verification → App Passwords.

---

## 📄 License

MIT
