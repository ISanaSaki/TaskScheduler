# 📅 Task Scheduler

A background task scheduling system built with **FastAPI**, **Celery**, and **WebSocket** support for real-time status tracking.

## ✨ Features

- ✅ Create and manage background tasks via REST API
- 🔁 Support for recurring tasks using **cron expressions**
- ⚡ Async task execution with **Celery** + **Redis**
- 📡 Real-time task status via **WebSocket**
- 🗄️ PostgreSQL database with **SQLModel** + **Alembic** migrations
- 🐳 Docker support for PostgreSQL and Redis

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Task Queue | Celery |
| Message Broker & Backend | Redis |
| Scheduler | APScheduler |
| ORM | SQLModel + SQLAlchemy |
| Migrations | Alembic |
| Database | PostgreSQL |
| Auth | JWT (python-jose) + Argon2 |

## 📁 Project Structure

TaskScheduler/

├── app/

│   ├── api/

│   │   └── routes/

│   │       ├── tasks.py      # REST endpoints

│   │       └── ws.py         # WebSocket endpoint

│   ├── core/

│   │   ├── config.py         # Settings & env vars

│   │   ├── database.py       # DB engine & session

│   │   ├── scheduler.py      # APScheduler setup

│   │   └── security.py       # JWT & password hashing

│   ├── models/

│   │   ├── task.py           # Task & TaskRun models

│   │   └── user.py           # User model

│   ├── schemas/

│   │   └── task.py           # Pydantic schemas

│   ├── worker/

│   │   ├── celery_app.py     # Celery configuration

│   │   └── tasks.py          # Celery task definitions

│   └── main.py

├── alembic/                  # DB migrations

├── .env.example

├── docker-compose.yml

├── Dockerfile

└── requirements.txt

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
# Edit .env and fill in your values
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

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/tasks/` | Create a new task |
| GET | `/tasks/` | List all tasks |
| GET | `/tasks/{id}/runs` | Get task run history |
| DELETE | `/tasks/{id}` | Delete a task |
| WS | `/ws/tasks/{id}` | Real-time task status |

## 🔁 Cron Example

```json
{
  "name": "Send weekly email",
  "cron_expression": "0 9 * * 5",
  "is_recurring": true
}
```

## 📄 License

MIT