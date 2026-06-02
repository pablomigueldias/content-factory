import pytest

from app.models.editorial import EditorialAngle
from app.models.video_job import VideoJob

pytestmark = pytest.mark.integration


def test_editorial_angle_one_per_job(db_session):
    job = VideoJob(topic="Por que o céu é azul")
    db_session.add(job)
    db_session.commit()

    angle = EditorialAngle(
        job_id=job.id,
        persona="Narrador curioso, tom de documentário descontraído",
        thesis="O céu azul é uma pista cotidiana sobre a física da luz.",
        hook="Você olha pro céu todo dia e nunca percebeu o que ele esconde.",
    )
    db_session.add(angle)
    db_session.commit()

    assert angle.id is not None
    assert angle.job_id == job.id