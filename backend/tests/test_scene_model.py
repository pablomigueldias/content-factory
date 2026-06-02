import pytest

from app.models.scene import Scene
from app.models.video_job import VideoJob

pytestmark = pytest.mark.integration


def test_scenes_belong_to_job_and_cascade(db_session):
    job = VideoJob(topic="Por que o céu é azul")
    db_session.add(job)
    db_session.commit()

    scenes = [
        Scene(job_id=job.id, position=0, narration="Gancho de abertura.",
              visual_description="Plano do céu ao amanhecer.", duration_seconds=8),
        Scene(job_id=job.id, position=1, narration="Desenvolvimento.",
              visual_description="Animação do espalhamento de Rayleigh.", duration_seconds=12),
    ]
    db_session.add_all(scenes)
    db_session.commit()

    scene_ids = [s.id for s in scenes]
    assert db_session.query(Scene).filter_by(job_id=job.id).count() == 2

    db_session.delete(job)
    db_session.commit()
    assert db_session.query(Scene).filter(Scene.id.in_(scene_ids)).count() == 0