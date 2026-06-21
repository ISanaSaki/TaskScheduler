import asyncio
from datetime import datetime
from app.worker.celery_app import celery_app

@celery_app.task(bind=True)
def run_task(self, task_id: int):
    from app.core.database import async_session
    from app.models.task import TaskRun, TaskStatus

    async def _run():
        async with async_session() as session:
            task_run = TaskRun(task_id=task_id, status=TaskStatus.running)
            session.add(task_run)
            await session.commit()
            await session.refresh(task_run)

            try:
                await asyncio.sleep(5)
                result = f"task {task_id} completed"

                task_run.status = TaskStatus.done
                task_run.result = result
                task_run.finished_at = datetime.utcnow()
            except Exception as e:
                task_run.status = TaskStatus.failed
                task_run.result = str(e)
                task_run.finished_at = datetime.utcnow()
            finally:
                await session.commit()

    asyncio.run(_run())