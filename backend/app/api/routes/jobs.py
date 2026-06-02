import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.video_job import VideoJob
from app.schemas.video_job import VideoJobCreate, VideoJobRead

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=VideoJobRead, status_code=status.HTTP_201_CREATED)
def create_job(payload: VideoJobCreate, db: Session = Depends(get_db)) -> VideoJob:
    job = VideoJob(topic=payload.topic)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("", response_model=list[VideoJobRead])
def list_jobs(db: Session = Depends(get_db)) -> list[VideoJob]:
    return list(db.scalars(select(VideoJob).order_by(VideoJob.created_at.desc())))


@router.get("/{job_id}", response_model=VideoJobRead)
def get_job(job_id: uuid.UUID, db: Session = Depends(get_db)) -> VideoJob:
    job = db.get(VideoJob, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job