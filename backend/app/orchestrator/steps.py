import logging

from sqlalchemy.orm import Session

from app.models.video_job import JobStatus, VideoJob
from app.orchestrator.research import run_research
from app.orchestrator.editorial import run_editorial
from app.orchestrator.scripting import run_scripting
from app.orchestrator.factcheck import run_factcheck

logger = logging.getLogger(__name__)


def _stub(step_name: str):
    def run(job: VideoJob, db: Session) -> None:
        logger.info("[%s] stub executado para job %s (tema=%r)", step_name, job.id, job.topic)
    return run

STEP_HANDLERS = {
    JobStatus.RESEARCHING: run_research,
    JobStatus.EDITORIAL: run_editorial,
    JobStatus.SCRIPTING: run_scripting,
    JobStatus.FACT_CHECKING: run_factcheck,
    JobStatus.NARRATING: _stub("narrating"),
    JobStatus.VISUALS: _stub("visuals"),
    JobStatus.EDITING: _stub("editing"),
    JobStatus.SUBTITLING: _stub("subtitling"),
    JobStatus.PUBLISHING: _stub("publishing"),
}