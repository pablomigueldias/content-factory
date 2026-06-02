import json
import logging

from sqlalchemy.orm import Session

from app.models.editorial import EditorialAngle
from app.models.fact import Fact
from app.models.source import Source
from app.models.video_job import VideoJob
from app.providers.gemini_client import GeminiProvider
from app.providers.llm import LLMProvider

logger = logging.getLogger(__name__)

EDITORIAL_PROMPT = """Você é um roteirista de um canal de curiosidades estilo Discovery, \
em português do Brasil. Recebeu uma lista de FATOS verificados sobre um tema. Sua missão \
é definir o ângulo editorial do vídeo — NÃO resumir os fatos, mas encontrar uma \
perspectiva única e cativante que os conecte.

TEMA: {topic}

FATOS VERIFICADOS:
{facts}

Defina três coisas:
1. PERSONA: quem narra e em que tom (1 frase). Ex.: "narrador curioso e levemente irônico".
2. TESE: a ideia central original que dá sentido ao vídeo (1-2 frases). Deve ser um ângulo, \
não um resumo. Conecte os fatos de forma inesperada.
3. GANCHO: a primeira frase do vídeo, feita pra prender nos 3 primeiros segundos.

Responda APENAS com JSON no formato EXATO:
{{"persona": "...", "thesis": "...", "hook": "..."}}
"""


def run_editorial(job: VideoJob, db: Session, llm: LLMProvider | None = None) -> None:
    llm = llm or GeminiProvider()

    facts = (
        db.query(Fact)
        .join(Source, Fact.source_id == Source.id)
        .filter(Source.job_id == job.id)
        .all()
    )
    if not facts:
        raise ValueError(f"Sem fatos para gerar ângulo editorial (job {job.id})")

    facts_text = "\n".join(f"- {f.content}" for f in facts)
    prompt = EDITORIAL_PROMPT.format(topic=job.topic, facts=facts_text)

    raw = llm.generate_text(prompt)
    data = _parse_editorial(raw)

    angle = EditorialAngle(
        job_id=job.id,
        persona=data["persona"],
        thesis=data["thesis"],
        hook=data["hook"],
    )
    db.add(angle)
    db.flush()

    logger.info("Ângulo editorial gerado para job %s: tese=%r", job.id, data["thesis"][:80])


def _parse_editorial(raw: str) -> dict:
    cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    data = json.loads(cleaned)
    for key in ("persona", "thesis", "hook"):
        if not data.get(key, "").strip():
            raise ValueError(f"Ângulo editorial sem '{key}': {raw[:200]}")
    return data