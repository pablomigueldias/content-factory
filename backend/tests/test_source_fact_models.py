import pytest

from app.models.fact import Fact
from app.models.source import Source, SourceType
from app.models.video_job import VideoJob

pytestmark = pytest.mark.integration


def test_source_with_facts_cascade(db_session):
    job = VideoJob(topic="Por que o céu é azul")
    db_session.add(job)
    db_session.commit()

    source = Source(
        job_id=job.id,
        source_type=SourceType.WIKIPEDIA,
        title="Espalhamento de Rayleigh",
        url="https://pt.wikipedia.org/wiki/Espalhamento_de_Rayleigh",
        raw_content="A luz azul é espalhada mais que a vermelha...",
    )
    source.facts = [
        Fact(content="A luz azul tem comprimento de onda menor."),
        Fact(content="O espalhamento é inversamente proporcional à 4ª potência do comprimento de onda."),
    ]
    db_session.add(source)
    db_session.commit()

    fact_ids = [f.id for f in source.facts]

    assert len(source.facts) == 2
  
    db_session.delete(source)
    db_session.commit()
    remaining = db_session.query(Fact).filter(Fact.id.in_(fact_ids)).count()
    assert remaining == 0
