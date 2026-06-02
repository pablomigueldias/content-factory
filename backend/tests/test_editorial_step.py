import pytest

from app.models.editorial import EditorialAngle
from app.models.fact import Fact
from app.models.source import Source, SourceType
from app.models.video_job import VideoJob
from app.orchestrator.editorial import _parse_editorial, run_editorial

pytestmark = pytest.mark.integration


class _FakeLLM:
    def __init__(self, response: str):
        self._response = response

    def generate_text(self, prompt: str) -> str:
        return self._response


def _seed_job_with_facts(db):
    job = VideoJob(topic="Por que o céu é azul")
    db.add(job)
    db.flush()
    source = Source(
        job_id=job.id, source_type=SourceType.WIKIPEDIA,
        title="Rayleigh", url="https://x", raw_content="...",
    )
    source.facts = [Fact(content="A luz azul é espalhada mais.")]
    db.add(source)
    db.commit()
    return job


def test_run_editorial_creates_angle(db_session):
    job = _seed_job_with_facts(db_session)
    fake = _FakeLLM('{"persona": "narrador curioso", "thesis": "uma tese", "hook": "um gancho"}')

    run_editorial(job, db_session, llm=fake)
    db_session.commit()

    angle = db_session.query(EditorialAngle).filter_by(job_id=job.id).one()
    assert angle.persona == "narrador curioso"
    assert angle.hook == "um gancho"


def test_run_editorial_without_facts_raises(db_session):
    job = VideoJob(topic="tema sem fatos")
    db_session.add(job)
    db_session.commit()

    with pytest.raises(ValueError, match="Sem fatos"):
        run_editorial(job, db_session, llm=_FakeLLM("{}"))


def test_parse_editorial_strips_markdown():
    raw = '```json\n{"persona": "p", "thesis": "t", "hook": "h"}\n```'
    assert _parse_editorial(raw) == {"persona": "p", "thesis": "t", "hook": "h"}


def test_parse_editorial_missing_field_raises():
    with pytest.raises(ValueError, match="thesis"):
        _parse_editorial('{"persona": "p", "thesis": "", "hook": "h"}')