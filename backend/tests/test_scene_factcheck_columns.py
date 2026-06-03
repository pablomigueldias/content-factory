import pytest

from app.models.fact import Fact
from app.models.scene import Scene
from app.models.source import Source, SourceType
from app.models.video_job import VideoJob

pytestmark = pytest.mark.integration


def _seed(db):
    job = VideoJob(topic="Por que o céu é azul")
    db.add(job)
    db.flush()
    source = Source(
        job_id=job.id, source_type=SourceType.WIKIPEDIA,
        title="t", url="https://x", raw_content="...",
    )
    source.facts = [Fact(content="A luz azul é espalhada mais.")]
    db.add(source)
    db.flush()
    return job, source.facts[0]


def test_scene_factcheck_fields_persist(db_session):
    job, fact = _seed(db_session)
    scene = Scene(
        job_id=job.id, position=0, narration="n", visual_description="v",
        duration_seconds=8, needs_review=True, review_reason="sem fonte",
        supporting_fact_id=fact.id,
    )
    db_session.add(scene)
    db_session.commit()
    db_session.refresh(scene)

    assert scene.needs_review is True
    assert scene.review_reason == "sem fonte"
    assert scene.supporting_fact_id == fact.id


def test_scene_default_needs_review_is_false(db_session):
    job, _ = _seed(db_session)
    scene = Scene(job_id=job.id, position=0, narration="n",
                  visual_description="v", duration_seconds=8)
    db_session.add(scene)
    db_session.commit()
    db_session.refresh(scene)
    assert scene.needs_review is False
    assert scene.supporting_fact_id is None


def test_supporting_fact_set_null_on_fact_delete(db_session):
    job, fact = _seed(db_session)
    scene = Scene(job_id=job.id, position=0, narration="n", visual_description="v",
                  duration_seconds=8, supporting_fact_id=fact.id)
    db_session.add(scene)
    db_session.commit()

    db_session.delete(fact)
    db_session.commit()
    db_session.refresh(scene)

    assert scene.supporting_fact_id is None