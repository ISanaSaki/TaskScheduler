from datetime import datetime
from app.worker.celery_app import celery_app

@celery_app.task(bind=True)
def run_task(self, task_id: int):
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from app.core.config import settings
    from app.models.user import User
    from app.models.task import Task, TaskRun, TaskStatus
    from app.core.email import send_email

    async def _run():
        # هر بار یه engine جدید میسازه تا مشکل Windows نداشته باشه
        engine = create_async_engine(settings.DATABASE_URL)
        session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with session_factory() as session:
            task_run = TaskRun(task_id=task_id, status=TaskStatus.running)
            session.add(task_run)

            task = await session.get(Task, task_id)
            if not task:
                await engine.dispose()
                return

            task.status = TaskStatus.running
            await session.commit()
            await session.refresh(task_run)

            try:
                await send_email(
                    to=task.email_to,
                    subject=task.email_subject,
                    body=task.email_body,
                )
                result = f"Email sent to {task.email_to}"
                task_run.status = TaskStatus.done
                task_run.result = result
                task_run.finished_at = datetime.utcnow()
                task.status = TaskStatus.done

            except Exception as e:
                task_run.status = TaskStatus.failed
                task_run.result = str(e)
                task_run.finished_at = datetime.utcnow()
                task.status = TaskStatus.failed

            finally:
                await session.commit()
                await engine.dispose()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_run())
    finally:
        loop.close()