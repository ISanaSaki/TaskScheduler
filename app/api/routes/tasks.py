from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.core.database import get_session
from app.models.task import Task, TaskRun, TaskStatus
from app.schemas.task import TaskCreate, TaskResponse, TaskRunResponse
from app.worker.tasks import run_task

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse)
async def create_task(data: TaskCreate, session: AsyncSession = Depends(get_session)):
    task = Task(**data.model_dump())
    session.add(task)
    await session.commit()
    await session.refresh(task)
    run_task.delay(task.id)
    return task

@router.get("/", response_model=list[TaskResponse])
async def get_tasks(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Task))
    return result.scalars().all()

@router.get("/{task_id}/runs", response_model=list[TaskRunResponse])
async def get_task_runs(task_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(TaskRun).where(TaskRun.task_id == task_id))
    return result.scalars().all()

@router.delete("/{task_id}")
async def delete_task(task_id: int, session: AsyncSession = Depends(get_session)):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await session.delete(task)
    await session.commit()
    return {"detail": "deleted"}