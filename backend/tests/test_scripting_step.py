import pytest

from app.models.editorial import EditorialAngle
from app.models.fact import Fact
from app.models.scene import Scene
from app.models.source import Source, SourceType
from app.models.video_job import VideoJob
from app.orchestrator.scripting import run_scripting

pytestmark = pytest.mark.integration


class _FakeLLM:
    def __init__(self, response: str):
        self._response = response

    def generate_text(self, prompt: str) -> str:
        return self._response


VALID_SCRIPT = (
    '{"scenes": ['
    '{"narration": "Você olha pro céu todo dia.", "visual_description": "Céu azul", "duration_seconds": 6},'
    '{"narration": "Mas nunca percebeu o que ele esconde.", "visual_description": "Luz dispersando", "duration_seconds": 10}'
    ']}'
)


def _seed_with_angle_and_facts(db):
    job = VideoJob(topic="Por que o céu é azul")
    db.add(job)
    db.flush()
    source = Source(
        job_id=job.id, source_type=SourceType.WIKIPEDIA,
        title="Rayleigh", url="https://x", raw_content="...",
    )
    source.facts = [Fact(content="A luz azul é espalhada mais.")]
    db.add(source)
    db.add(EditorialAngle(
        job_id=job.id, persona="narrador curioso",
        thesis="uma tese", hook="Você olha pro céu todo dia.",
    ))
    db.commit()
    return job


def test_run_scripting_creates_ordered_scenes(db_session):
    job = _seed_with_angle_and_facts(db_session)
    run_scripting(job, db_session, llm=_FakeLLM(VALID_SCRIPT))
    db_session.commit()

    scenes = (
        db_session.query(Scene).filter_by(job_id=job.id).order_by(Scene.position).all()
    )
    assert [s.position for s in scenes] == [0, 1]
    assert scenes[0].narration == "Você olha pro céu todo dia."
    assert scenes[1].duration_seconds == 10


def test_run_scripting_without_angle_raises(db_session):
    job = VideoJob(topic="tema sem ângulo")
    db_session.add(job)
    db_session.flush()
    source = Source(
        job_id=job.id, source_type=SourceType.WIKIPEDIA,
        title="t", url="https://x", raw_content="...",
    )
    source.facts = [Fact(content="um fato")]
    db_session.add(source)
    db_session.commit()

    with pytest.raises(ValueError, match="ângulo"):
        run_scripting(job, db_session, llm=_FakeLLM(VALID_SCRIPT))


def test_run_scripting_without_facts_raises(db_session):
    job = VideoJob(topic="tema sem fatos")
    db_session.add(job)
    db_session.flush()
    db_session.add(EditorialAngle(job_id=job.id, persona="p", thesis="t", hook="h"))
    db_session.commit()

    with pytest.raises(ValueError, match="fatos"):
        run_scripting(job, db_session, llm=_FakeLLM(VALID_SCRIPT))