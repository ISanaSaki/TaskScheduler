# 📅 Task Scheduler

A background task scheduling system built with **FastAPI**, **Celery**, and **WebSocket** support for real-time status tracking.

## ✨ Features

- ✅ Create and manage background tasks via REST API
- 🔁 Support for recurring tasks using **cron expressions**
- ⚡ Async task execution with **Celery** + **Redis**
- 📡 Real-time task status via **WebSocket** (JWT-authenticated)
- 🗄️ PostgreSQL database with **SQLModel** + **Alembic** migrations
- 🐳 Docker support for PostgreSQL and Redis
- 🔐 JWT authentication (register/login) with Argon2 password hashing

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

## 📁 Project Structure

```
TaskScheduler/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py       # Register & login endpoints
│   │       ├── tasks.py      # REST endpoints
│   │       └── ws.py         # WebSocket endpoint (JWT-authenticated)
│   ├── core/
│   │   ├── config.py         # Settings & env vars
│   │   ├── database.py       # DB engine & session
│   │   ├── scheduler.py      # APScheduler setup
│   │   └── security.py       # JWT & password hashing
│   ├── models/
│   │   ├── task.py           # Task & TaskRun models
│   │   └── user.py           # User model
│   ├── schemas/
│   │   ├── auth.py           # Auth schemas
│   │   └── task.py           # Task/TaskRun schemas
│   ├── worker/
│   │   ├── celery_app.py     # Celery configuration
│   │   └── tasks.py          # Celery task definitions
│   └── main.py
├── alembic/                  # DB migrations
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
# Edit .env and fill in your values (at minimum POSTGRES_PASSWORD and SECRET_KEY)
```

### 2. Start PostgreSQL & Redis

```bash
docker compose up -d
```

### 3. Apply migrations

```bash
alembic upgrade head
```

### 4. Start Celery worker (new terminal)

```bash
celery -A app.worker.celery_app.celery_app worker --loglevel=info --pool=solo
```

### 5. Start API server (new terminal)

```bash
uvicorn app.main:app --reload
```

---

## 📡 API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | None | Register a new user |
| POST | `/auth/login` | None | Login and receive JWT token |
| POST | `/tasks/` | Bearer JWT | Create a new task |
| GET | `/tasks/` | Bearer JWT | List your tasks |
| GET | `/tasks/{id}/runs` | Bearer JWT | Get task run history |
| DELETE | `/tasks/{id}` | Bearer JWT | Delete a task |
| WS | `/ws/tasks/{id}?token=<jwt>` | Query JWT | Real-time task status |

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

Returns `{"access_token": "...", "token_type": "bearer"}` — use the token for subsequent requests.

---

## 🔁 Cron Example

Recurring tasks are scheduled via APScheduler when created and re-loaded on server restart:

```json
{
  "name": "Send weekly email",
  "cron_expression": "0 9 * * 5",
  "is_recurring": true
}
```

One-off tasks (no cron) are dispatched to Celery immediately:

```json
{
  "name": "Process report",
  "is_recurring": false
}
```

---

## 📡 WebSocket Usage

Connect with the JWT token as a query parameter:

```
ws://localhost:8000/ws/tasks/{task_id}?token=<your_jwt_token>
```

You can use `test_ws.html` in the repo root for a quick browser test.

Messages received:

```json
{ "task_id": 1, "status": "running", "result": null }
{ "task_id": 1, "status": "done", "result": "task 1 completed successfully" }
```

The connection closes automatically once the task reaches `done` or `failed`.

---

## 📄 License

MIT