import os
from typing import Optional
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import File, BookMetadata
from app.schemas.file import FileListResponse, FileResponse
from app.services.metadata_service import MetadataService
from app.utils.file_utils import detect_format, compute_file_hash, SUPPORTED_FORMATS
from app.core.storage import storage


class FileService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upload_file(self, filename: str, file_data: bytes) -> File:
        fmt = detect_format(filename)
        if fmt is None:
            raise ValueError(f"不支持的文件格式: {filename}")

        # 写入临时文件以计算哈希
        ext = os.path.splitext(filename)[1].lower()
        temp_path = os.path.join(storage.get_absolute_path(storage.temp_dir), f"upload_{id(file_data)}{ext}")
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(file_data)

        try:
            file_hash = compute_file_hash(temp_path)

            # 检查是否已存在相同文件
            result = await self.db.execute(select(File).where(File.hash == file_hash))
            existing = result.scalar_one_or_none()
            if existing:
                os.remove(temp_path)
                return existing

            # 保存到存储
            storage_path = await storage.save_upload(file_data, ext)
            # 如果 temp_path 和 storage_path 不同，删除 temp
            if temp_path != storage_path:
                os.remove(temp_path)

            file = File(
                filename=filename,
                format=fmt,
                size=len(file_data),
                hash=file_hash,
                storage_path=storage_path,
            )
            self.db.add(file)
            await self.db.flush()

            # 创建空的元数据记录
            metadata = BookMetadata(file_id=file.id)
            self.db.add(metadata)
            await self.db.commit()
            await self.db.refresh(file)
            return file
        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

    async def list_files(
        self, page: int = 1, page_size: int = 20, sort: str = "created_at_desc"
    ) -> FileListResponse:
        order = File.created_at.desc() if sort == "created_at_desc" else File.created_at.asc()

        total_q = select(func.count(File.id))
        total_result = await self.db.execute(total_q)
        total = total_result.scalar() or 0

        q = select(File).order_by(order).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(q)
        files = result.scalars().all()

        return FileListResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[FileResponse.model_validate(f) for f in files],
        )

    async def get_file(self, file_id: str) -> Optional[File]:
        result = await self.db.execute(select(File).where(File.id == file_id))
        return result.scalar_one_or_none()

    async def delete_file(self, file_id: str) -> bool:
        result = await self.db.execute(select(File).where(File.id == file_id))
        file = result.scalar_one_or_none()
        if not file:
            return False

        # 删除物理文件
        if storage.file_exists(file.storage_path):
            await storage.delete_file(file.storage_path)

        # 级联删除 metadata 和 tasks
        await self.db.execute(delete(File).where(File.id == file_id))
        await self.db.commit()
        return True

    async def get_file_path(self, file_id: str) -> Optional[str]:
        file = await self.get_file(file_id)
        if not file:
            return None
        return file.storage_path
