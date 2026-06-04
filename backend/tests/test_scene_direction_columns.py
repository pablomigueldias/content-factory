import pytest

from app.models.scene import Scene
from app.models.video_job import VideoJob

pytestmark = pytest.mark.integration


def _seed_job(db):
    job = VideoJob(topic="Por que o céu é azul")
    db.add(job)
    db.flush()
    return job


def test_scene_direction_fields_persist(db_session):
    job = _seed_job(db_session)
    scene = Scene(
        job_id=job.id, position=0, narration="n", visual_description="v",
        duration_seconds=8,
        storyboard="Bolonhesa encara a câmera e revira os olhos.",
        camera_movement="zoom_in",
        camera_intensity="aggressive",
        framing="close_up",
        expression_slug="deboche",
        pose_slug="bracos-cruzados",
        gaze_direction="to_camera",
        emotion="deboche crescente",
        image_prompt="flat 2D cartoon, contorno grosso, cores chapadas, Bolonhesa...",
        animation_prompt="leve balanço de ombros + zoom in agressivo",
        cut_plan={
            "transition_in": "hard_cut",
            "transition_out": "whip_pan",
            "cut_speed": "fast",
            "impact_moment_seconds": 2.4,
            "notes": "corte seco no 'mas'",
        },
        narration_cues={
            "pauses": [{"after_word": "framework", "duration_ms": 400}],
            "emphasis": ["rápido", "sozinho"],
            "tone": "debochado_crescente",
        },
    )
    db_session.add(scene)
    db_session.commit()
    db_session.refresh(scene)

    assert scene.storyboard.startswith("Bolonhesa")
    assert scene.camera_movement == "zoom_in"
    assert scene.camera_intensity == "aggressive"
    assert scene.framing == "close_up"
    assert scene.expression_slug == "deboche"
    assert scene.pose_slug == "bracos-cruzados"
    assert scene.gaze_direction == "to_camera"
    assert scene.emotion == "deboche crescente"
    assert scene.image_prompt.startswith("flat 2D cartoon")
    assert scene.animation_prompt.endswith("agressivo")
    assert scene.cut_plan["transition_out"] == "whip_pan"
    assert scene.cut_plan["impact_moment_seconds"] == 2.4
    assert scene.narration_cues["emphasis"] == ["rápido", "sozinho"]
    assert scene.narration_cues["pauses"][0]["duration_ms"] == 400


def test_scene_direction_fields_default_to_none(db_session):
    job = _seed_job(db_session)
    scene = Scene(job_id=job.id, position=0, narration="n",
                  visual_description="v", duration_seconds=8)
    db_session.add(scene)
    db_session.commit()
    db_session.refresh(scene)

    assert scene.storyboard is None
    assert scene.camera_movement is None
    assert scene.camera_intensity is None
    assert scene.framing is None
    assert scene.expression_slug is None
    assert scene.pose_slug is None
    assert scene.gaze_direction is None
    assert scene.emotion is None
    assert scene.image_prompt is None
    assert scene.animation_prompt is None
    assert scene.cut_plan is None
    assert scene.narration_cues is None
