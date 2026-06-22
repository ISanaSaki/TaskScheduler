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
            add_recurring_task(task.id, task.cron_expression)

def add_recurring_task(task_id: int, cron_expression: str):
    job_id = f"task_{task_id}"
    scheduler.add_job(
        run_task.delay,
        CronTrigger.from_crontab(cron_expression),
        args=[task_id],
        id=job_id,
        replace_existing=True,
    )

def remove_recurring_task(task_id: int):
    job_id = f"task_{task_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

def start_scheduler():
    scheduler.start()
