import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.file import FileListResponse, FileResponse, FormatsResponse
from app.services.file_service import FileService
from app.utils.file_utils import SUPPORTED_FORMATS, format_compatibility
from app.config import settings

router = APIRouter()


@router.post("/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名为空")

    file_data = await file.read()
    if len(file_data) > settings.file_max_size:
        raise HTTPException(
            status_code=413,
            detail=f"文件大小超过限制（最大 {settings.file_max_size // 1024 // 1024}MB）",
        )
    if len(file_data) == 0:
        raise HTTPException(status_code=400, detail="文件为空")

    service = FileService(db)
    try:
        result = await service.upload_file(file.filename, file_data)
        return FileResponse.model_validate(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=FileListResponse)
async def list_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort: str = Query("created_at_desc", pattern="^(created_at_desc|created_at_asc)$"),
    db: AsyncSession = Depends(get_db),
):
    service = FileService(db)
    return await service.list_files(page=page, page_size=page_size, sort=sort)


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(file_id: str, db: AsyncSession = Depends(get_db)):
    service = FileService(db)
    file = await service.get_file(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse.model_validate(file)


@router.delete("/{file_id}", status_code=204)
async def delete_file(file_id: str, db: AsyncSession = Depends(get_db)):
    service = FileService(db)
    deleted = await service.delete_file(file_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="文件不存在")


@router.get("/{file_id}/download")
async def download_file(file_id: str, db: AsyncSession = Depends(get_db)):
    from fastapi.responses import FileResponse as FastAPIFileResponse

    service = FileService(db)
    file = await service.get_file(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="文件不存在")

    if not os.path.isfile(file.storage_path):
        raise HTTPException(status_code=410, detail="文件已过期")

    filename = os.path.splitext(file.filename)[0] + "." + file.format
    return FastAPIFileResponse(
        path=file.storage_path,
        filename=filename,
        media_type="application/octet-stream",
    )


@router.get("/{file_id}/cover")
async def get_cover(file_id: str, db: AsyncSession = Depends(get_db)):
    from fastapi.responses import FileResponse as FastAPIFileResponse

    from app.services.metadata_service import MetadataService

    service = MetadataService(db)
    meta = await service.get_metadata(file_id)
    if not meta or not meta.cover_url:
        raise HTTPException(status_code=404, detail="封面不存在")

    cover_path = meta.cover_url.lstrip("/api/v1/files/").rstrip("/cover")
    # cover_url 是相对路径格式，需要重新查询实际路径
    from sqlalchemy import select
    from app.models import BookMetadata

    result = await db.execute(
        select(BookMetadata).where(BookMetadata.file_id == file_id)
    )
    meta_obj = result.scalar_one_or_none()
    if not meta_obj or not meta_obj.cover_path:
        raise HTTPException(status_code=404, detail="封面不存在")

    return FastAPIFileResponse(
        path=meta_obj.cover_path,
        media_type="image/jpeg",
    )


@router.get("/formats/all", response_model=FormatsResponse)
async def get_formats():
    matrix = format_compatibility()
    return FormatsResponse(
        supported_formats=sorted(SUPPORTED_FORMATS),
        conversion_matrix=matrix,
    )
