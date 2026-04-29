import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _task_id() -> str:
    return f"t_{uuid.uuid4().hex[:8]}"


class ConversionTask(Base):
    __tablename__ = "conversion_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_task_id)
    file_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("files.id", ondelete="CASCADE"), nullable=False
    )
    batch_id: Mapped[str | None] = mapped_column(String(36), index=True)
    source_format: Mapped[str] = mapped_column(String(20), nullable=False)
    target_format: Mapped[str] = mapped_column(String(20), nullable=False)
    options: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    progress_message: Mapped[str | None] = mapped_column(String(500))
    error_code: Mapped[str | None] = mapped_column(String(50))
    error_message: Mapped[str | None] = mapped_column(Text)
    output_file_id: Mapped[str | None] = mapped_column(String(36))
    calibre_output: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)

    file = relationship("File", back_populates="tasks")
