import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class JobStatus(str, enum.Enum):

    PENDING = "pending"
    RESEARCHING = "researching"
    EDITORIAL = "editorial"
    SCRIPTING = "scripting"
    FACT_CHECKING = "fact_checking"
    NARRATING = "narrating"
    VISUALS = "visuals"
    EDITING = "editing"
    SUBTITLING = "subtitling"
    READY_FOR_REVIEW = "ready_for_review"
    PUBLISHING = "publishing"
    DONE = "done"
    FAILED = "failed"


class VideoJob(Base):

    __tablename__ = "video_jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    topic: Mapped[str] = mapped_column(String(500))
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status"),
        default=JobStatus.PENDING,
        index=True, 
        )
    error: Mapped[str | None] = mapped_column(String(2000), default=None)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<VideoJob {self.id} topic={self.topic!r} status={self.status.value} >"
