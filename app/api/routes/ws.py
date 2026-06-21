import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlmodel import select
from app.core.database import async_session
from app.models.task import TaskRun, TaskStatus

router = APIRouter()

@router.websocket("/ws/tasks/{task_id}")
async def task_status(websocket: WebSocket, task_id: int):
    await websocket.accept()
    try:
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
    finally:
        await websocket.close()