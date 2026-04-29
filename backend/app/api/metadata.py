from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.metadata import MetadataResponse, MetadataUpdate
from app.services.metadata_service import MetadataService

router = APIRouter()


@router.get("/{file_id}", response_model=MetadataResponse)
async def get_metadata(file_id: str, db: AsyncSession = Depends(get_db)):
    service = MetadataService(db)
    meta = await service.get_metadata(file_id)
    if not meta:
        raise HTTPException(status_code=404, detail="元数据不存在")
    return meta


@router.put("/{file_id}", response_model=MetadataResponse)
async def update_metadata(
    file_id: str,
    data: MetadataUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = MetadataService(db)
    meta = await service.update_metadata(file_id, data)
    if not meta:
        raise HTTPException(status_code=404, detail="元数据不存在")
    return meta


@router.post("/{file_id}/cover", response_model=dict)
async def upload_cover(
    file_id: str,
    cover: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    data = await cover.read()
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="封面图片不能超过 5MB")
    if cover.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=400, detail="仅支持 JPG 和 PNG 格式")

    service = MetadataService(db)
    cover_path = await service.upload_cover(file_id, data)
    if not cover_path:
        raise HTTPException(status_code=404, detail="文件不存在")
    return {"cover_url": f"/api/v1/files/{file_id}/cover"}
