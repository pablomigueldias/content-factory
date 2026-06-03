import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class EditorialAngle(Base):
    __tablename__ = "editorial_angles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("video_jobs.id", ondelete="CASCADE"), unique=True, index=True
    )

    persona: Mapped[str] = mapped_column(String(500))
    thesis: Mapped[str] = mapped_column(Text)
    hook: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )