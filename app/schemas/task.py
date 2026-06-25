from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.task import TaskStatus

class TaskCreate(BaseModel):
    name: str
    cron_expression: Optional[str] = None
    is_recurring: bool = False
    email_to: Optional[str] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None

class TaskResponse(BaseModel):
    id: int
    name: str
    cron_expression: Optional[str] = None
    is_recurring: bool
    status: TaskStatus
    created_at: datetime

    class Config:
        from_attributes = True

class TaskRunResponse(BaseModel):
    id: int
    task_id: int
    status: TaskStatus
    result: Optional[str] = None
    started_at: datetime
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True
