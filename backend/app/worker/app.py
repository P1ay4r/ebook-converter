"""Celery 应用实例。"""

from celery import Celery

from app.config import settings

celery_app = Celery(
    "ebook_converter",
    broker=settings.redis_url,
    backend=settings.redis_url,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
)

# 默认配置
celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
