from datetime import datetime
from pydantic import BaseModel, Field


class MetadataResponse(BaseModel):
    file_id: str
    title: str | None = None
    author: str | None = None
    language: str | None = None
    isbn: str | None = None
    publisher: str | None = None
    pub_date: str | None = None
    tags: list[str] | None = None
    description: str | None = None
    cover_url: str | None = None
    updated_at: datetime

    model_config = {"from_attributes": True}


class MetadataUpdate(BaseModel):
    title: str | None = Field(None, max_length=500)
    author: str | None = Field(None, max_length=200)
    language: str | None = None
    isbn: str | None = Field(None, max_length=20)
    publisher: str | None = Field(None, max_length=200)
    pub_date: str | None = None
    tags: list[str] | None = None
    description: str | None = Field(None, max_length=5000)
