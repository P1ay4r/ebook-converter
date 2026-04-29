import json
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import BookMetadata, File
from app.schemas.metadata import MetadataResponse, MetadataUpdate
from app.core.storage import storage


class MetadataService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_metadata(self, file_id: str) -> Optional[MetadataResponse]:
        result = await self.db.execute(
            select(BookMetadata).where(BookMetadata.file_id == file_id)
        )
        meta = result.scalar_one_or_none()
        if not meta:
            return None

        return self._to_response(meta)

    async def update_metadata(self, file_id: str, data: MetadataUpdate) -> Optional[MetadataResponse]:
        result = await self.db.execute(
            select(BookMetadata).where(BookMetadata.file_id == file_id)
        )
        meta = result.scalar_one_or_none()
        if not meta:
            return None

        update_data = data.model_dump(exclude_unset=True)
        if "tags" in update_data and update_data["tags"] is not None:
            update_data["tags"] = json.dumps(update_data["tags"], ensure_ascii=False)

        for key, value in update_data.items():
            setattr(meta, key, value)

        await self.db.commit()
        await self.db.refresh(meta)
        return self._to_response(meta)

    async def upload_cover(self, file_id: str, cover_data: bytes) -> Optional[str]:
        result = await self.db.execute(
            select(BookMetadata).where(BookMetadata.file_id == file_id)
        )
        meta = result.scalar_one_or_none()
        if not meta:
            return None

        cover_path = await storage.save_cover(cover_data)
        meta.cover_path = cover_path
        await self.db.commit()
        return cover_path

    def _to_response(self, meta: BookMetadata) -> MetadataResponse:
        tags = None
        if meta.tags:
            try:
                tags = json.loads(meta.tags)
            except (json.JSONDecodeError, TypeError):
                tags = [meta.tags] if meta.tags else None

        cover_url = None
        if meta.cover_path:
            cover_url = f"/api/v1/files/{meta.file_id}/cover"

        return MetadataResponse(
            file_id=meta.file_id,
            title=meta.title,
            author=meta.author,
            language=meta.language,
            isbn=meta.isbn,
            publisher=meta.publisher,
            pub_date=meta.pub_date,
            tags=tags,
            description=meta.description,
            cover_url=cover_url,
            updated_at=meta.updated_at,
        )
