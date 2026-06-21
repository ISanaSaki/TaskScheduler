from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, ForeignKey

class TaskStatus(str, Enum):
    pending = "pending"
    running = "running"
    done = "done"
    failed = "failed"

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    )
    name: str
    cron_expression: Optional[str] = None
    is_recurring: bool = False
    status: TaskStatus = TaskStatus.pending
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TaskRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(
        sa_column=Column(Integer, ForeignKey("task.id", ondelete="CASCADE"))
    )
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.running
    result: Optional[str] = None