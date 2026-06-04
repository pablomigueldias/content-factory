import json

import pytest

from app.models.editorial import EditorialAngle
from app.models.scene import Scene
from app.models.video_job import VideoJob
from app.orchestrator.direction import run_direction

pytestmark = pytest.mark.integration


class _FakeLLM:
    def __init__(self, response: str):
        self._response = response
        self.prompts: list[str] = []

    def generate_text(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self._response


def _direction(position: int, expression: str, pose: str) -> dict:
    return {
        "position": position,
        "storyboard": f"cena {position}: encara a câmera",
        "camera_movement": "zoom_in",
        "camera_intensity": "medium",
        "framing": "close_up",
        "expression_slug": expression,
        "pose_slug": pose,
        "gaze_direction": "to_camera",
        "emotion": "deboche",
        "image_prompt": "flat 2D cartoon, contorno grosso, Bolonhesa encarando",
        "animation_prompt": "leve balanço + zoom in",
        "cut_plan": {
            "transition_in": "hard_cut", "transition_out": "whip_pan",
            "cut_speed": "fast", "impact_moment_seconds": 2.0, "notes": "seco",
        },
        "narration_cues": {
            "pauses": [{"after_word": "isso", "duration_ms": 300}],
            "emphasis": ["rápido"], "tone": "debochado",
        },
    }


def _plan(*directions: dict) -> str:
    return json.dumps({"scenes": list(directions)})


def _seed(db, n=2):
    job = VideoJob(topic="Por que o céu é azul")
    db.add(job)
    db.flush()
    db.add(EditorialAngle(job_id=job.id, persona="debochado",
                          thesis="uma tese", hook="Você olha pro céu."))
    for i in range(n):
        db.add(Scene(job_id=job.id, position=i, narration="n",
                     bravata="bravata", verdade_tecnica="verdade",
                     visual_description="v", duration_seconds=8))
    db.commit()
    return job


def test_run_direction_fills_all_fields(db_session):
    job = _seed(db_session, n=2)
    llm = _FakeLLM(_plan(
        _direction(0, "deboche", "bracos-cruzados"),
        _direction(1, "nerd", "apontando"),
    ))

    run_direction(job, db_session, llm=llm)
    db_session.commit()

    scenes = db_session.query(Scene).filter_by(
        job_id=job.id).order_by(Scene.position).all()
    assert scenes[0].expression_slug == "deboche"
    assert scenes[0].pose_slug == "bracos-cruzados"
    assert scenes[0].camera_movement == "zoom_in"
    assert scenes[0].framing == "close_up"
    assert scenes[0].image_prompt.startswith("flat 2D cartoon")
    assert scenes[0].cut_plan["transition_out"] == "whip_pan"
    assert scenes[0].narration_cues["emphasis"] == ["rápido"]
    assert scenes[1].expression_slug == "nerd"
    assert all(not s.needs_review for s in scenes)
    # O prompt deve carregar o estilo do manifesto e os slugs disponíveis.
    assert "flat 2D cartoon" in llm.prompts[0]
    assert "neutro" in llm.prompts[0]


def test_invalid_slug_falls_back_and_flags_review(db_session):
    job = _seed(db_session, n=1)
    llm = _FakeLLM(_plan(_direction(0, "expressao-inexistente", "pose-inexistente")))

    run_direction(job, db_session, llm=llm)
    db_session.commit()

    scene = db_session.query(Scene).filter_by(job_id=job.id).one()
    assert scene.expression_slug == "neutro"  # fallback seguro
    assert scene.pose_slug is None
    assert scene.needs_review is True
    assert "inválido" in scene.review_reason
    # Mesmo no fallback, os demais campos de direção foram preenchidos.
    assert scene.storyboard is not None
    assert scene.camera_movement == "zoom_in"


def test_scene_without_direction_is_flagged(db_session):
    job = _seed(db_session, n=2)
    # LLM só dirige a cena 0; a cena 1 fica sem direção.
    llm = _FakeLLM(_plan(_direction(0, "deboche", "apontando")))

    run_direction(job, db_session, llm=llm)
    db_session.commit()

    scenes = db_session.query(Scene).filter_by(
        job_id=job.id).order_by(Scene.position).all()
    assert scenes[0].needs_review is False
    assert scenes[1].needs_review is True
    assert scenes[1].review_reason is not None


def test_run_direction_without_scenes_raises(db_session):
    job = VideoJob(topic="sem cenas")
    db_session.add(job)
    db_session.flush()
    db_session.add(EditorialAngle(job_id=job.id, persona="p", thesis="t", hook="h"))
    db_session.commit()

    with pytest.raises(ValueError, match="cenas"):
        run_direction(job, db_session, llm=_FakeLLM(_plan(_direction(0, "neutro", "apontando"))))


def test_run_direction_without_angle_raises(db_session):
    job = VideoJob(topic="sem ângulo")
    db_session.add(job)
    db_session.flush()
    db_session.add(Scene(job_id=job.id, position=0, narration="n",
                         visual_description="v", duration_seconds=8))
    db_session.commit()

    with pytest.raises(ValueError, match="ângulo"):
        run_direction(job, db_session, llm=_FakeLLM(_plan(_direction(0, "neutro", "apontando"))))
