import uuid
from datetime import datetime

from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    false,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Scene(Base):
    __tablename__ = "scenes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("video_jobs.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(Integer)
    narration: Mapped[str] = mapped_column(Text)
    bravata: Mapped[str | None] = mapped_column(Text, default=None)
    verdade_tecnica: Mapped[str | None] = mapped_column(Text, default=None)
    visual_description: Mapped[str] = mapped_column(Text)
    duration_seconds: Mapped[int] = mapped_column(Integer)

    needs_review: Mapped[bool] = mapped_column(
        Boolean, server_default=false(), default=False
    )
    review_reason: Mapped[str | None] = mapped_column(String(500), default=None)
    audio_path: Mapped[str | None] = mapped_column(String(1000), default=None)
    supporting_fact_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("facts.id", ondelete="SET NULL"), index=True, default=None
    )

    # Direção criativa (preenchida pela etapa de direção; toda nullable para que
    # cenas antigas continuem válidas, mesma estratégia de verdade_tecnica).
    storyboard: Mapped[str | None] = mapped_column(Text, default=None)
    camera_movement: Mapped[str | None] = mapped_column(String(50), default=None)
    camera_intensity: Mapped[str | None] = mapped_column(String(20), default=None)
    framing: Mapped[str | None] = mapped_column(String(50), default=None)
    expression_slug: Mapped[str | None] = mapped_column(String(50), default=None)
    pose_slug: Mapped[str | None] = mapped_column(String(50), default=None)
    gaze_direction: Mapped[str | None] = mapped_column(String(30), default=None)
    emotion: Mapped[str | None] = mapped_column(String(50), default=None)
    image_prompt: Mapped[str | None] = mapped_column(Text, default=None)
    animation_prompt: Mapped[str | None] = mapped_column(Text, default=None)
    cut_plan: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=None)
    narration_cues: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=None)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )