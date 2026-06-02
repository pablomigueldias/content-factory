import logging

from sqlalchemy.orm import Session

from app.models.video_job import JobStatus, VideoJob

logger = logging.getLogger(__name__)


def _stub(step_name: str):
    def run(job: VideoJob, db: Session) -> None:
        logger.info("[%s] stub executado para job %s (tema=%r)", step_name, job.id, job.topic)
    return run

STEP_HANDLERS = {
    JobStatus.RESEARCHING: _stub("researching"),
    JobStatus.EDITORIAL: _stub("editorial"),
    JobStatus.SCRIPTING: _stub("scripting"),
    JobStatus.FACT_CHECKING: _stub("fact_checking"),
    JobStatus.NARRATING: _stub("narrating"),
    JobStatus.VISUALS: _stub("visuals"),
    JobStatus.EDITING: _stub("editing"),
    JobStatus.SUBTITLING: _stub("subtitling"),
    JobStatus.PUBLISHING: _stub("publishing"),
}