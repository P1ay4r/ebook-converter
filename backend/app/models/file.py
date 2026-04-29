import uuid
from datetime import datetime, timedelta

from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _file_id() -> str:
    return f"f_{uuid.uuid4().hex[:8]}"


def _default_expires() -> datetime:
    return datetime.utcnow() + timedelta(hours=24)


class File(Base):
    __tablename__ = "files"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_file_id)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    format: Mapped[str] = mapped_column(String(20), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    hash: Mapped[str] = mapped_column(String(128), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="uploaded")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, default=_default_expires)

    metadata_rel = relationship("BookMetadata", back_populates="file", uselist=False, cascade="all, delete-orphan")
    tasks = relationship("ConversionTask", back_populates="file", cascade="all, delete-orphan")
