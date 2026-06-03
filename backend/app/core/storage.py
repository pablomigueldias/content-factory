import uuid
from pathlib import Path

from app.core.config import settings


def scene_audio_path(job_id: uuid.UUID, position: int) -> Path:
    job_dir = Path(settings.media_root) / str(job_id)
    job_dir.mkdir(parents=True, exist_ok=True)
    return job_dir / f"scene_{position:02d}.wav"