from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlmodel import select
from app.core.database import async_session
from app.models.task import Task
from app.worker.tasks import run_task

scheduler = AsyncIOScheduler()

async def load_recurring_tasks():
    async with async_session() as session:
        result = await session.execute(
            select(Task).where(Task.is_recurring == True)
        )
        tasks = result.scalars().all()

    for task in tasks:
        if task.cron_expression:
            scheduler.add_job(
                run_task.delay,
                CronTrigger.from_crontab(task.cron_expression),
                args=[task.id],
                id=f"task_{task.id}",
                replace_existing=True,
            )

def start_scheduler():
    scheduler.start()