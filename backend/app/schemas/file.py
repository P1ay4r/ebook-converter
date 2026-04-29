from datetime import datetime
from pydantic import BaseModel


class FileResponse(BaseModel):
    id: str
    filename: str
    format: str
    size: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class FileListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[FileResponse]


class FormatInfo(BaseModel):
    source: str
    targets: list[str]


class FormatsResponse(BaseModel):
    supported_formats: list[str]
    conversion_matrix: dict[str, list[str]]
