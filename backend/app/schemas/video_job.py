import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.video_job import JobStatus


class VideoJobCreate(BaseModel):
    topic: str = Field(min_length=3, max_length=500)


class VideoJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    topic: str
    status: JobStatus
    error: str | None
    created_at: datetime
    updated_at: datetime