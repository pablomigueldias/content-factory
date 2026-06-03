import logging

from sqlalchemy.orm import Session

from app.core.storage import scene_audio_path
from app.models.scene import Scene
from app.models.video_job import VideoJob
from app.providers.chatterbox_tts import ChatterboxProvider
from app.providers.tts import TTSProvider

logger = logging.getLogger(__name__)


def run_narration(job: VideoJob, db: Session, tts: TTSProvider | None = None) -> None:
    tts = tts or ChatterboxProvider()

    scenes = (
        db.query(Scene).filter_by(job_id=job.id).order_by(Scene.position).all()
    )
    if not scenes:
        raise ValueError(f"Sem cenas para narrar (job {job.id})")

    try:
        for scene in scenes:
            out_path = scene_audio_path(job.id, scene.position)
            tts.synthesize(scene.narration, str(out_path))
            scene.audio_path = str(out_path)
            db.flush()
            logger.info("Cena %d narrada -> %s", scene.position, out_path)
    finally:
        tts.unload()

    logger.info("Narração concluída para job %s: %d cenas.", job.id, len(scenes))