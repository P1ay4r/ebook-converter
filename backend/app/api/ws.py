import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.redis import get_redis

router = APIRouter()


class ConnectionManager:
    """管理 WebSocket 连接，按 task_id 分组。"""

    def __init__(self):
        self.active: dict[str, set[WebSocket]] = {}

    async def connect(self, task_id: str, ws: WebSocket):
        await ws.accept()
        self.active.setdefault(task_id, set()).add(ws)

    def disconnect(self, task_id: str, ws: WebSocket):
        self.active.get(task_id, set()).discard(ws)
        if not self.active.get(task_id):
            self.active.pop(task_id, None)

    async def send_json(self, task_id: str, data: dict):
        for ws in list(self.active.get(task_id, set())):
            try:
                await ws.send_json(data)
            except Exception:
                self.active.get(task_id, set()).discard(ws)


manager = ConnectionManager()


@router.websocket("/task/{task_id}")
async def task_websocket(websocket: WebSocket, task_id: str):
    await manager.connect(task_id, websocket)
    redis = await get_redis()
    last_progress = -1

    try:
        while True:
            # 从 Redis 获取进度
            progress = await redis.get(f"task:{task_id}:progress")
            if progress is not None:
                progress = int(progress)
            else:
                progress = 0

            # 获取状态 (从 task key)
            status = await redis.get(f"task:{task_id}:status")

            if progress != last_progress or status:
                await websocket.send_json({
                    "type": "progress",
                    "task_id": task_id,
                    "progress": progress,
                    "status": status or "unknown",
                })
                last_progress = progress

            if status in ("completed", "failed", "cancelled"):
                break

            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(task_id, websocket)
