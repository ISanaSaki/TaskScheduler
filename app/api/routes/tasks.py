from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.core.database import get_session
from app.core.security import get_current_user
from app.core.scheduler import scheduler, add_recurring_task, remove_recurring_task
from app.models.task import Task, TaskRun, TaskStatus
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskRunResponse
from app.worker.tasks import run_task
from app.core.logger import get_logger

logger = get_logger("tasks")

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    data: TaskCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    task = Task(**data.model_dump(), user_id=current_user.id)
    session.add(task)
    await session.commit()
    await session.refresh(task)

    if task.is_recurring and task.cron_expression:
        add_recurring_task(task.id, task.cron_expression)
        logger.info(f"Recurring task {task.id} scheduled - cron: '{task.cron_expression}' - user: '{current_user.username}'")
    else:
        run_task.delay(task.id)
        logger.info(f"Task {task.id} created and dispatched to Celery - user: '{current_user.username}'")

    return task

@router.get("/", response_model=list[TaskResponse])
async def get_tasks(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    result = await session.execute(
        select(Task).where(Task.user_id == current_user.id)
    )
    return result.scalars().all()

@router.get("/{task_id}/runs", response_model=list[TaskRunResponse])
async def get_task_runs(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user.id:
        logger.warning(f"Access denied - user '{current_user.username}' tried to access task {task_id}")
        raise HTTPException(status_code=403, detail="Access denied")

    result = await session.execute(
        select(TaskRun).where(TaskRun.task_id == task_id).order_by(TaskRun.id.desc())
    )
    return result.scalars().all()

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user.id:
        logger.warning(f"Access denied - user '{current_user.username}' tried to delete task {task_id}")
        raise HTTPException(status_code=403, detail="Access denied")

    if task.is_recurring:
        remove_recurring_task(task.id)

    await session.delete(task)
    await session.commit()
    logger.info(f"Task {task_id} deleted by user '{current_user.username}'")
    return {"detail": "deleted"}