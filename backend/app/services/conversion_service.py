import json
import uuid
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import File, ConversionTask
from app.schemas.conversion import (
    ConversionStartRequest,
    TaskResponse,
    BatchStartResponse,
    BatchStatusResponse,
)
from app.utils.file_utils import is_compatible, format_compatibility


class ConversionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def start_conversion(
        self, request: ConversionStartRequest
    ) -> BatchStartResponse:
        batch_id = f"batch_{uuid.uuid4().hex[:8]}"
        tasks: list[TaskResponse] = []

        for file_id in request.file_ids:
            result = await self.db.execute(select(File).where(File.id == file_id))
            file = result.scalar_one_or_none()
            if not file:
                continue

            if not is_compatible(file.format, request.target_format):
                tasks.append(
                    TaskResponse(
                        task_id="",
                        file_id=file_id,
                        status="failed",
                        error_message=f"不支持将 {file.format} 转换为 {request.target_format}",
                    )
                )
                continue

            task = ConversionTask(
                file_id=file_id,
                batch_id=batch_id,
                source_format=file.format,
                target_format=request.target_format,
                options=request.options.model_dump_json() if request.options else None,
                status="pending",
            )
            self.db.add(task)
            await self.db.flush()
            tasks.append(self._task_to_response(task))

        await self.db.commit()
        return BatchStartResponse(batch_id=batch_id, tasks=tasks)

    async def get_task(self, task_id: str) -> Optional[TaskResponse]:
        result = await self.db.execute(
            select(ConversionTask).where(ConversionTask.id == task_id)
        )
        task = result.scalar_one_or_none()
        return self._task_to_response(task) if task else None

    async def get_batch_status(self, batch_id: str) -> Optional[BatchStatusResponse]:
        result = await self.db.execute(
            select(ConversionTask).where(ConversionTask.batch_id == batch_id)
        )
        tasks = result.scalars().all()
        if not tasks:
            return None

        task_responses = [self._task_to_response(t) for t in tasks]
        statuses = [t.status for t in tasks]

        return BatchStatusResponse(
            batch_id=batch_id,
            total=len(tasks),
            completed=statuses.count("completed"),
            failed=statuses.count("failed"),
            processing=statuses.count("processing"),
            pending=statuses.count("pending"),
            tasks=task_responses,
        )

    async def cancel_task(self, task_id: str) -> Optional[TaskResponse]:
        result = await self.db.execute(
            select(ConversionTask).where(ConversionTask.id == task_id)
        )
        task = result.scalar_one_or_none()
        if not task or task.status not in ("pending", "processing"):
            return None

        task.status = "cancelled"
        await self.db.commit()
        return self._task_to_response(task)

    async def update_task_progress(
        self, task_id: str, progress: int, message: str = ""
    ):
        result = await self.db.execute(
            select(ConversionTask).where(ConversionTask.id == task_id)
        )
        task = result.scalar_one_or_none()
        if task:
            task.progress = progress
            task.progress_message = message
            await self.db.commit()

    async def mark_task_completed(self, task_id: str, output_file_id: str):
        result = await self.db.execute(
            select(ConversionTask).where(ConversionTask.id == task_id)
        )
        task = result.scalar_one_or_none()
        if task:
            from datetime import datetime

            task.status = "completed"
            task.progress = 100
            task.output_file_id = output_file_id
            task.completed_at = datetime.utcnow()
            await self.db.commit()

    async def mark_task_failed(self, task_id: str, code: str, message: str):
        result = await self.db.execute(
            select(ConversionTask).where(ConversionTask.id == task_id)
        )
        task = result.scalar_one_or_none()
        if task:
            from datetime import datetime

            task.status = "failed"
            task.error_code = code
            task.error_message = message
            task.completed_at = datetime.utcnow()
            await self.db.commit()

    def _task_to_response(self, task: ConversionTask) -> TaskResponse:
        return TaskResponse(
            task_id=task.id,
            file_id=task.file_id,
            status=task.status,
            progress=task.progress,
            progress_message=task.progress_message or "",
            source_format=task.source_format,
            target_format=task.target_format,
            created_at=task.created_at,
            completed_at=task.completed_at,
            error_message=task.error_message,
            output_file_id=task.output_file_id,
        )
