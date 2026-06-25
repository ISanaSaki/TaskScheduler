import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, WebSocketException, status, Query
from sqlmodel import select
from jose import jwt, JWTError
from app.core.database import async_session
from app.core.config import settings
from app.models.task import Task, TaskRun, TaskStatus

router = APIRouter()

async def get_ws_user(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

@router.websocket("/ws/tasks/{task_id}")
async def task_status(
    websocket: WebSocket,
    task_id: int,
    token: str = Query(..., description="JWT access token")
):
    username = await get_ws_user(token)
    if not username:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or missing token")

    await websocket.accept()

    try:
        async with async_session() as session:
            from app.models.user import User
            user_result = await session.execute(select(User).where(User.username == username))
            user = user_result.scalars().first()
            if not user:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return

            task = await session.get(Task, task_id)
            if not task or task.user_id != user.id:
                await websocket.send_json({"error": "Task not found or access denied"})
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return

        while True:
            async with async_session() as session:
                result = await session.execute(
                    select(TaskRun)
                    .where(TaskRun.task_id == task_id)
                    .order_by(TaskRun.id.desc())
                )
                run = result.scalars().first()

            if run:
                await websocket.send_json({
                    "task_id": task_id,
                    "status": run.status.value,
                    "result": run.result,
                })
                if run.status in (TaskStatus.done, TaskStatus.failed):
                    break
            else:
                await websocket.send_json({
                    "task_id": task_id,
                    "status": "no runs yet",
                    "result": None
                })

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        pass
    except Exception:
        pass