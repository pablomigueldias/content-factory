import logging

from sqlalchemy.orm import Session

from app.models.fact import Fact
from app.models.scene import Scene
from app.models.source import Source
from app.models.video_job import VideoJob
from app.providers.bge_reranker import BGEReranker
from app.providers.verifier import Verifier

logger = logging.getLogger(__name__)


def run_factcheck(job: VideoJob, db: Session, verifier: Verifier | None = None) -> None:
    verifier = verifier or BGEReranker()

    scenes = (
        db.query(Scene).filter_by(job_id=job.id).order_by(Scene.position).all()
    )
    if not scenes:
        raise ValueError(f"Sem cenas para fazer fact-check (job {job.id})")

    facts = (
        db.query(Fact)
        .join(Source, Fact.source_id == Source.id)
        .filter(Source.job_id == job.id)
        .all()
    )
    if not facts:
        raise ValueError(f"Sem fatos para fazer fact-check (job {job.id})")

    fact_texts = [f.content for f in facts]
    used_fact_ids: set = set()
    flagged = 0

    for scene in scenes:
        # Só a camada técnica é checada; a bravata é deboche da persona, não fato.
        claim = scene.verdade_tecnica or scene.narration
        result = verifier.ground(claim, fact_texts)

        if result.verified and result.fact_index is not None:
            supporting = facts[result.fact_index]
            scene.supporting_fact_id = supporting.id
            scene.needs_review = False
            scene.review_reason = None
            used_fact_ids.add(supporting.id)
        else:
            scene.supporting_fact_id = None
            scene.needs_review = True
            scene.review_reason = (
                f"Sem fonte suficiente (melhor score={result.score:.2f})"
            )
            flagged += 1

    for fact in facts:
        if fact.id in used_fact_ids:
            fact.verified = True

    db.flush()

    logger.info(
        "Fact-check do job %s: %d cenas, %d sinalizadas p/ revisão, %d fatos usados.",
        job.id, len(scenes), flagged, len(used_fact_ids),
    )