"""
定时清理任务 - 在 FastAPI 中作为后台任务运行。
"""

import asyncio
import logging

from app.services.cleanup_service import CleanupService

logger = logging.getLogger(__name__)


async def periodic_cleanup(interval_seconds: int = 1800):
    """
    每 30 分钟清理一次过期文件。
    在 FastAPI 启动时作为后台任务运行。
    """
    while True:
        try:
            count = await CleanupService.cleanup_expired()
            if count > 0:
                logger.info(f"已清理 {count} 个过期文件")
        except Exception as e:
            logger.error(f"清理任务异常: {e}")
        await asyncio.sleep(interval_seconds)
