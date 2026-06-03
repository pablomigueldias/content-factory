import uuid

from app.core import storage


def test_scene_audio_path_builds_padded_filename(tmp_path, monkeypatch):
    monkeypatch.setattr(storage.settings, "media_root", str(tmp_path))
    job_id = uuid.uuid4()

    path = storage.scene_audio_path(job_id, 3)

    assert path.name == "scene_03.wav"
    assert path.parent.name == str(job_id)
    assert path.parent.exists()


def test_scene_audio_path_same_inputs_same_path(tmp_path, monkeypatch):
    monkeypatch.setattr(storage.settings, "media_root", str(tmp_path))
    job_id = uuid.uuid4()
    assert storage.scene_audio_path(job_id, 0) == storage.scene_audio_path(job_id, 0)