import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class SourceType(str, enum.Enum):
    WIKIPEDIA = "wikipedia"
    WIKIMEDIA = "wikimedia"
    REDDIT = "reddit"
    WEB = "web"


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("video_jobs.id", ondelete="CASCADE"), index=True
    )
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType, name="source_type"))
    title: Mapped[str] = mapped_column(String(500))
    url: Mapped[str] = mapped_column(String(1000))
    raw_content: Mapped[str] = mapped_column(Text)  

    reliability: Mapped[int] = mapped_column(Integer, default=50)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )  

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    facts: Mapped[list["Fact"]] = relationship(
        back_populates="source", cascade="all, delete-orphan"
    )