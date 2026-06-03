import logging
from functools import lru_cache

from app.core.config import settings
from app.providers.verifier import GroundingResult

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _load_model(model_name: str, device: str):
    from sentence_transformers import CrossEncoder
    logger.info("Carregando reranker %s em %s...", model_name, device)
    return CrossEncoder(model_name, device=device or None, max_length=512)


def _resolve_device(configured: str) -> str:
    if configured:
        return configured
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


class BGEReranker:
    def __init__(self, model_name: str | None = None, threshold: float | None = None,
                 device: str | None = None):
        self.model_name = model_name or settings.reranker_model
        self.threshold = threshold if threshold is not None else settings.factcheck_threshold
        self.device = _resolve_device(
            device if device is not None else settings.reranker_device
        )

    def ground(self, claim: str, candidate_facts: list[str]) -> GroundingResult:
        if not candidate_facts:
            return GroundingResult(fact_index=None, score=0.0, verified=False)

        model = _load_model(self.model_name, self.device)
        pairs = [(claim, fact) for fact in candidate_facts]
        scores = model.predict(pairs)

        best_index = max(range(len(scores)), key=lambda i: scores[i])
        best_score = float(scores[best_index])
        verified = best_score >= self.threshold

        return GroundingResult(
            fact_index=best_index if verified else None,
            score=best_score,
            verified=verified,
        )