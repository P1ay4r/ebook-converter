from datetime import datetime, timedelta
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import File
from app.core.database import async_session_factory
from app.core.storage import storage


class CleanupService:
    """定时清理过期文件。"""

    @staticmethod
    async def cleanup_expired():
        """清理 24 小时前的文件。"""
        cutoff = datetime.utcnow() - timedelta(hours=24)

        async with async_session_factory() as db:
            result = await db.execute(
                select(File).where(File.created_at < cutoff)
            )
            expired_files = result.scalars().all()

            for f in expired_files:
                if storage.file_exists(f.storage_path):
                    await storage.delete_file(f.storage_path)

            await db.execute(delete(File).where(File.created_at < cutoff))
            await db.commit()

        return len(expired_files)
