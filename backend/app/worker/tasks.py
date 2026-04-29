"""
Celery 转换任务定义。

转换任务在 Celery Worker 进程中执行，通过 Redis 与 FastAPI 通信。
进度通过 Redis 更新，WebSocket 路由轮询 Redis 后推送给前端。
"""

import asyncio
import os
import json
from datetime import datetime

import redis as sync_redis

from app.config import settings
from app.worker.app import celery_app
from app.worker.converter import convert_ebook, is_calibre_available
from app.utils.file_utils import get_file_ext

# 同步 Redis 连接（Celery Worker 是同步的）
_redis = sync_redis.from_url(settings.redis_url, decode_responses=True)


def update_progress(task_id: str, percent: int, message: str = ""):
    """更新 Redis 中的任务进度和状态。"""
    _redis.set(f"task:{task_id}:progress", percent)
    _redis.set(f"task:{task_id}:message", message)
    _redis.expire(f"task:{task_id}:progress", 86400)
    _redis.expire(f"task:{task_id}:message", 86400)


def set_status(task_id: str, status: str):
    """更新任务状态。"""
    _redis.set(f"task:{task_id}:status", status)
    _redis.expire(f"task:{task_id}:status", 86400)


@celery_app.task(bind=True, max_retries=1, acks_late=True)
def convert_file_task(self, task_id: str, input_path: str, target_format: str, options: dict | None):
    """
    转换任务 - 在主 Worker 进程中执行。

    参数由 FastAPI 的 conversion API 在提交任务时传入。
    """
    if not is_calibre_available():
        set_status(task_id, "failed")
        _redis.set(f"task:{task_id}:error", "Calibre 未安装")
        return {"status": "failed", "error": "calibre_not_found"}

    output_ext = get_file_ext(target_format)
    output_path = os.path.join(settings.temp_dir, f"{task_id}{output_ext}")
    os.makedirs(settings.temp_dir, exist_ok=True)

    set_status(task_id, "processing")
    update_progress(task_id, 1, "正在解析源文件...")

    # 同步方式运行异步转换器
    async def run():
        async for event in convert_ebook(input_path, output_path, options):
            if event["type"] == "progress":
                update_progress(task_id, event["percent"], event.get("message", ""))
            elif event["type"] == "complete":
                update_progress(task_id, 100, "转换完成")
                set_status(task_id, "completed")

                # 将输出文件移动到存储目录
                from app.core.storage import storage
                output_ext_full = get_file_ext(target_format)
                dest_path = asyncio.run(storage.save_output(output_path, output_ext_full))

                # 更新数据库（通过直接 SQLite 操作）
                from app.core.database import async_session_factory
                from app.models import ConversionTask
                from sqlalchemy import select

                async with async_session_factory() as db:
                    result = await db.execute(
                        select(ConversionTask).where(ConversionTask.id == task_id)
                    )
                    task = result.scalar_one_or_none()
                    if task:
                        task.status = "completed"
                        task.progress = 100
                        task.output_file_id = dest_path
                        task.completed_at = datetime.utcnow()
                        await db.commit()

                return {"status": "completed", "output_path": dest_path}

            elif event["type"] == "error":
                error_msg = event.get("message", "未知错误")
                update_progress(task_id, 0, error_msg)
                set_status(task_id, "failed")
                _redis.set(f"task:{task_id}:error", error_msg)

                # 更新数据库错误状态
                from app.core.database import async_session_factory
                from app.models import ConversionTask
                from sqlalchemy import select

                async with async_session_factory() as db:
                    result = await db.execute(
                        select(ConversionTask).where(ConversionTask.id == task_id)
                    )
                    task = result.scalar_one_or_none()
                    if task:
                        task.status = "failed"
                        task.error_code = event.get("code", "unknown")
                        task.error_message = error_msg
                        task.completed_at = datetime.utcnow()
                        await db.commit()

                return {"status": "failed", "error": error_msg}

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run())
        loop.close()
        return result
    except Exception as e:
        set_status(task_id, "failed")
        _redis.set(f"task:{task_id}:error", str(e))
        return {"status": "failed", "error": str(e)}


def submit_conversion_task(task_id: str):
    """
    从 FastAPI 端调用，将任务提交到 Celery 队列。
    因为跨进程通信，我们通过 Redis 传递必要信息。
    """
    # 从 DB 读取任务信息
    # 注意：这里是跨进程边界，我们需要通过同步方式读取信息
    # 实际使用中，Celery 任务从参数获取信息
    from app.core.database import async_session_factory
    from app.models import ConversionTask, File
    from sqlalchemy import select

    async def _submit():
        async with async_session_factory() as db:
            result = await db.execute(
                select(ConversionTask).where(ConversionTask.id == task_id)
            )
            task = result.scalar_one_or_none()
            if not task:
                return

            file_result = await db.execute(
                select(File).where(File.id == task.file_id)
            )
            file = file_result.scalar_one_or_none()
            if not file:
                return

            options = {}
            if task.options:
                try:
                    options = json.loads(task.options)
                except json.JSONDecodeError:
                    pass

            # 提交异步任务到 Celery
            convert_file_task.delay(
                task_id,
                file.storage_path,
                task.target_format,
                options,
            )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_submit())
    loop.close()
