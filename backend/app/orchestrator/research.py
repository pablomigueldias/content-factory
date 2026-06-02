import logging

from sqlalchemy.orm import Session

from app.models.fact import Fact
from app.models.video_job import VideoJob
from app.providers.ollama_client import extract_facts
from app.providers.wikipedia import result_to_source, search_wikipedia

logger = logging.getLogger(__name__)


def run_research(job: VideoJob, db: Session) -> None:
    result = search_wikipedia(job.topic)
    if result is None or not result.raw_content.strip():
        raise ValueError(f"Nenhuma fonte encontrada na Wikipedia para: {job.topic!r}")

    source = result_to_source(result, job_id=job.id)
    db.add(source)
    db.flush()

    fact_texts = extract_facts(source.raw_content)
    if not fact_texts:
        raise ValueError(f"Nenhum fato extraído da fonte: {result.title!r}")

    db.add_all([Fact(source_id=source.id, content=text) for text in fact_texts])
    db.flush()

    logger.info(
        "Pesquisa OK para job %s: fonte=%r, %d fatos.",
        job.id, result.title, len(fact_texts),
    )