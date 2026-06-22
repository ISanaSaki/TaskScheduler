from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.core.database import get_session
from app.core.security import get_current_user
from app.models.task import Task, TaskRun, TaskStatus
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskRunResponse
from app.worker.tasks import run_task

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
    run_task.delay(task.id)
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
        raise HTTPException(status_code=403, detail="Access denied")

    result = await session.execute(
        select(TaskRun).where(TaskRun.task_id == task_id)
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
        raise HTTPException(status_code=403, detail="Access denied")

    await session.delete(task)
    await session.commit()
    return {"detail": "deleted"}