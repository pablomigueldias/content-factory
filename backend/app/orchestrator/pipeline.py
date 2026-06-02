import logging

from sqlalchemy.orm import Session

from app.models.video_job import JobStatus, VideoJob
from app.orchestrator.steps import STEP_HANDLERS

logger = logging.getLogger(__name__)


PIPELINE_ORDER: list[JobStatus] = [
    JobStatus.RESEARCHING,
    JobStatus.EDITORIAL,
    JobStatus.SCRIPTING,
    JobStatus.FACT_CHECKING,
    JobStatus.NARRATING,
    JobStatus.VISUALS,
    JobStatus.EDITING,
    JobStatus.SUBTITLING,
    JobStatus.READY_FOR_REVIEW,
]


def run_pipeline(job: VideoJob, db: Session) -> None:
    try:
        for step in PIPELINE_ORDER:
            job.status = step
            db.commit()

            handler = STEP_HANDLERS.get(step)
            if handler is not None:
                handler(job, db)


            if step is JobStatus.READY_FOR_REVIEW:
                logger.info("Job %s aguardando revisão humana.", job.id)
                break
    except Exception as exc:  
        logger.exception("Falha no pipeline do job %s", job.id)
        job.status = JobStatus.FAILED
        job.error = str(exc)[:2000]
        db.commit()
        raise