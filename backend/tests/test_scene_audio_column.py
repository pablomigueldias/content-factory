import pytest

from app.models.scene import Scene
from app.models.video_job import VideoJob

pytestmark = pytest.mark.integration


def test_audio_path_persists_and_defaults_none(db_session):
    job = VideoJob(topic="Por que o céu é azul")
    db_session.add(job)
    db_session.commit()

    scene = Scene(job_id=job.id, position=0, narration="n",
                  visual_description="v", duration_seconds=8)
    db_session.add(scene)
    db_session.commit()
    db_session.refresh(scene)
    assert scene.audio_path is None          # default

    scene.audio_path = "media/abc/scene_00.wav"
    db_session.commit()
    db_session.refresh(scene)
    assert scene.audio_path == "media/abc/scene_00.wav"