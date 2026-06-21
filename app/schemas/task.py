from pydantic import BaseModel
from typing import Optional
from app.models.task import TaskStatus

class TaskCreate(BaseModel):
    name: str
    cron_expression: Optional[str] = None
    is_recurring: bool = False

class TaskResponse(BaseModel):
    id: int
    name: str
    cron_expression: Optional[str] = None
    is_recurring: bool
    status: TaskStatus

    class Config:
        from_attributes = True

class TaskRunResponse(BaseModel):
    id: int
    task_id: int
    status: TaskStatus
    result: Optional[str] = None

    class Config:
        from_attributes = True