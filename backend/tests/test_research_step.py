import pytest

from app.models.fact import Fact
from app.models.source import Source
from app.models.video_job import VideoJob
from app.orchestrator import research as research_mod
from app.providers.wikipedia import WikipediaResult

pytestmark = pytest.mark.integration


def test_run_research_saves_source_and_facts(db_session, monkeypatch):
    monkeypatch.setattr(
        research_mod, "search_wikipedia",
        lambda topic: WikipediaResult(
            title="Buraco negro",
            url="https://pt.wikipedia.org/wiki/Buraco_negro",
            raw_content="Buracos negros são objetos densos dos quais a luz não escapa.",
        ),
    )
    monkeypatch.setattr(
        research_mod, "extract_facts",
        lambda text: ["A luz não escapa de um buraco negro.", "Buracos negros são densos."],
    )

    job = VideoJob(topic="o que é um buraco negro")
    db_session.add(job)
    db_session.commit()

    research_mod.run_research(job, db_session)
    db_session.commit()

    sources = db_session.query(Source).filter_by(job_id=job.id).all()
    assert len(sources) == 1
    assert sources[0].reliability == 80
    assert db_session.query(Fact).filter_by(source_id=sources[0].id).count() == 2


def test_run_research_raises_when_no_source(db_session, monkeypatch):
    monkeypatch.setattr(research_mod, "search_wikipedia", lambda topic: None)

    job = VideoJob(topic="asdkjhqweqwe")
    db_session.add(job)
    db_session.commit()

    with pytest.raises(ValueError, match="Nenhuma fonte"):
        research_mod.run_research(job, db_session)