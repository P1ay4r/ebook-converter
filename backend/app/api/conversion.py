from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.conversion import (
    ConversionStartRequest,
    TaskResponse,
    BatchStartResponse,
    BatchStatusResponse,
)
from app.services.conversion_service import ConversionService
from app.worker.tasks import submit_conversion_task

router = APIRouter()


@router.post("/start", response_model=BatchStartResponse)
async def start_conversion(
    request: ConversionStartRequest,
    db: AsyncSession = Depends(get_db),
):
    service = ConversionService(db)
    batch = await service.start_conversion(request)

    # 提交到 Celery
    for task in batch.tasks:
        if task.task_id:
            submit_conversion_task(task.task_id)

    return batch


@router.get("/task/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    service = ConversionService(db)
    task = await service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.get("/batch/{batch_id}", response_model=BatchStatusResponse)
async def get_batch(batch_id: str, db: AsyncSession = Depends(get_db)):
    service = ConversionService(db)
    batch = await service.get_batch_status(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")
    return batch


@router.post("/task/{task_id}/cancel", response_model=TaskResponse)
async def cancel_task(task_id: str, db: AsyncSession = Depends(get_db)):
    service = ConversionService(db)
    task = await service.cancel_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在或无法取消")
    return task
