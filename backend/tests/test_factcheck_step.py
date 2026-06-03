import pytest

from app.models.fact import Fact
from app.models.scene import Scene
from app.models.source import Source, SourceType
from app.models.video_job import VideoJob
from app.orchestrator.factcheck import run_factcheck
from app.providers.verifier import GroundingResult

pytestmark = pytest.mark.integration


class _ScriptedVerifier:

    def __init__(self, results: list[GroundingResult]):
        self._results = iter(results)

    def ground(self, claim, candidate_facts):
        return next(self._results)


def _seed(db, n_scenes=2):
    job = VideoJob(topic="Por que o céu é azul")
    db.add(job)
    db.flush()
    source = Source(
        job_id=job.id, source_type=SourceType.WIKIPEDIA,
        title="t", url="https://x", raw_content="...",
    )
    source.facts = [
        Fact(content="A luz azul é espalhada mais."),
        Fact(content="O Sol emite luz branca."),
    ]
    db.add(source)
    db.flush()
    for i in range(n_scenes):
        db.add(Scene(job_id=job.id, position=i, narration=f"cena {i}",
                     visual_description="v", duration_seconds=8))
    db.commit()
    return job, source.facts


def test_factcheck_marks_supported_and_flagged(db_session):
    job, facts = _seed(db_session, n_scenes=2)
    verifier = _ScriptedVerifier([
        GroundingResult(fact_index=0, score=0.9, verified=True),
        GroundingResult(fact_index=None, score=0.2, verified=False),
    ])

    run_factcheck(job, db_session, verifier=verifier)
    db_session.commit()

    scenes = db_session.query(Scene).filter_by(
        job_id=job.id).order_by(Scene.position).all()
    assert scenes[0].supporting_fact_id == facts[0].id
    assert scenes[0].needs_review is False
    assert scenes[1].needs_review is True
    assert "score=0.20" in scenes[1].review_reason

    db_session.refresh(facts[0])
    db_session.refresh(facts[1])
    assert facts[0].verified is True
    assert facts[1].verified is False


def test_factcheck_is_idempotent(db_session):
    job, facts = _seed(db_session, n_scenes=1)
    flagged = [GroundingResult(fact_index=None, score=0.1, verified=False)]
    run_factcheck(job, db_session, verifier=_ScriptedVerifier(flagged))
    db_session.commit()

    run_factcheck(job, db_session,
                  verifier=_ScriptedVerifier([GroundingResult(fact_index=0, score=0.8, verified=True)]))
    db_session.commit()

    scene = db_session.query(Scene).filter_by(job_id=job.id).one()
    assert scene.needs_review is False
    assert scene.supporting_fact_id == facts[0].id
    assert scene.review_reason is None


def test_factcheck_without_scenes_raises(db_session):
    job = VideoJob(topic="sem cenas")
    db_session.add(job)
    db_session.flush()
    source = Source(job_id=job.id, source_type=SourceType.WIKIPEDIA,
                    title="t", url="https://x", raw_content="...")
    source.facts = [Fact(content="um fato")]
    db_session.add(source)
    db_session.commit()

    with pytest.raises(ValueError, match="cenas"):
        run_factcheck(job, db_session, verifier=_ScriptedVerifier([]))
