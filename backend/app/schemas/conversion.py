from datetime import datetime
from pydantic import BaseModel, Field


class ConversionOptions(BaseModel):
    margin_top: int | None = Field(None, ge=0)
    margin_bottom: int | None = Field(None, ge=0)
    margin_left: int | None = Field(None, ge=0)
    margin_right: int | None = Field(None, ge=0)
    base_font_size: int | None = Field(None, ge=8, le=72)
    line_height: float | None = Field(None, ge=1.0, le=3.0)
    embed_fonts: bool | None = None
    compression_level: int | None = Field(None, ge=0, le=9)
    remove_paragraph_spacing: bool | None = None
    extra_css: str | None = None


class ConversionStartRequest(BaseModel):
    file_ids: list[str] = Field(..., min_length=1, max_length=50)
    target_format: str = Field(..., min_length=2, max_length=10)
    options: ConversionOptions | None = None


class TaskResponse(BaseModel):
    task_id: str
    file_id: str
    status: str
    progress: int = 0
    progress_message: str | None = None
    source_format: str | None = None
    target_format: str | None = None
    created_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
    output_file_id: str | None = None

    model_config = {"from_attributes": True}


class BatchStartResponse(BaseModel):
    batch_id: str
    tasks: list[TaskResponse]


class BatchStatusResponse(BaseModel):
    batch_id: str
    total: int
    completed: int
    failed: int
    processing: int
    pending: int
    tasks: list[TaskResponse]
