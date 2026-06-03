import pytest

from app.models.video_job import JobStatus, VideoJob
from app.orchestrator.pipeline import run_pipeline

pytestmark = pytest.mark.integration


def _recording_handlers(call_log: list):
    def make(step_name):
        def handler(job, db):
            call_log.append(step_name)
        return handler
    return {
        JobStatus.RESEARCHING: make("researching"),
        JobStatus.EDITORIAL: make("editorial"),
        JobStatus.SCRIPTING: make("scripting"),
        JobStatus.FACT_CHECKING: make("fact_checking"),
        JobStatus.NARRATING: make("narrating"),
    }


def test_pipeline_runs_steps_in_order_and_stops_at_review(db_session):
    job = VideoJob(topic="Por que os gatos ronronam")
    db_session.add(job)
    db_session.commit()

    calls: list = []
    run_pipeline(job, db_session, handlers=_recording_handlers(calls))

    assert calls == ["researching", "editorial", "scripting", "fact_checking", "narrating"]
    assert job.status == JobStatus.READY_FOR_REVIEW
    assert job.error is None


def test_pipeline_marks_failed_on_handler_error(db_session):
    job = VideoJob(topic="tema que vai falhar")
    db_session.add(job)
    db_session.commit()

    def boom(job, db):
        raise RuntimeError("falha simulada na etapa")

    handlers = {JobStatus.RESEARCHING: boom}

    with pytest.raises(RuntimeError, match="falha simulada"):
        run_pipeline(job, db_session, handlers=handlers)

    assert job.status == JobStatus.FAILED
    assert "falha simulada" in job.error #type: ignore