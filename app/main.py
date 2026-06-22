from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import init_db
from app.api.routes.tasks import router as tasks_router
from app.api.routes.ws import router as ws_router
from app.api.routes.auth import router as auth_router
from app.core.scheduler import scheduler, start_scheduler, load_recurring_tasks

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await load_recurring_tasks()
    start_scheduler()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(ws_router)