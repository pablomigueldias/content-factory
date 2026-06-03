import pytest

from app.models.scene import Scene
from app.models.video_job import VideoJob
from app.orchestrator.narration import run_narration

pytestmark = pytest.mark.integration


class _FakeTTS:
    """Registra as chamadas e cria um arquivo vazio, sem tocar em modelo/GPU."""
    def __init__(self):
        self.synth_calls = []
        self.unloaded = False

    def synthesize(self, text: str, out_path: str) -> None:
        self.synth_calls.append((text, out_path))
        with open(out_path, "wb") as f:
            f.write(b"")

    def unload(self) -> None:
        self.unloaded = True


class _FailingTTS(_FakeTTS):
    def synthesize(self, text: str, out_path: str) -> None:
        raise RuntimeError("boom no modelo")


def _seed_scenes(db, n=2):
    job = VideoJob(topic="Por que o céu é azul")
    db.add(job)
    db.flush()
    for i in range(n):
        db.add(Scene(job_id=job.id, position=i, narration=f"narração da cena {i}",
                     visual_description="v", duration_seconds=8))
    db.commit()
    return job


def test_run_narration_synthesizes_each_scene(db_session, tmp_path, monkeypatch):
    monkeypatch.setattr("app.core.storage.settings.media_root", str(tmp_path))
    job = _seed_scenes(db_session, n=3)
    fake = _FakeTTS()

    run_narration(job, db_session, tts=fake)
    db_session.commit()

    scenes = db_session.query(Scene).filter_by(job_id=job.id).order_by(Scene.position).all()
    assert len(fake.synth_calls) == 3
    assert all(s.audio_path is not None for s in scenes)
    assert scenes[0].audio_path.endswith("scene_00.wav")
    assert fake.synth_calls[0][0] == "narração da cena 0"


def test_run_narration_unloads_even_on_failure(db_session, tmp_path, monkeypatch):
    monkeypatch.setattr("app.core.storage.settings.media_root", str(tmp_path))
    job = _seed_scenes(db_session, n=2)
    failing = _FailingTTS()

    with pytest.raises(RuntimeError, match="boom"):
        run_narration(job, db_session, tts=failing)

    assert failing.unloaded is True


def test_run_narration_without_scenes_raises(db_session):
    job = VideoJob(topic="sem cenas")
    db_session.add(job)
    db_session.commit()

    with pytest.raises(ValueError, match="cenas"):
        run_narration(job, db_session, tts=_FakeTTS())