from app.models.video_job import JobStatus, VideoJob
from app.orchestrator.pipeline import run_pipeline

import pytest

pytestmark = pytest.mark.integration


def test_pipeline_stops_at_review(db_session):
    job = VideoJob(topic="Por que os gatos ronronam")
    db_session.add(job)
    db_session.commit()

    run_pipeline(job, db_session)

    assert job.status == JobStatus.READY_FOR_REVIEW
    assert job.error is None


def test_run_endpoint(client):
    created = client.post("/jobs", json={"topic": "Como nascem os furacoes"}).json()
    response = client.post(f"/jobs/{created['id']}/run")
    assert response.status_code == 200
    assert response.json()["status"] == "ready_for_review"