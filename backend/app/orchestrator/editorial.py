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

EDITORIAL_PROMPT = """Você é o roteirista-chefe do canal do GORDÃO BOLONHESA, um canal \
faceless de TI e programação em português do Brasil, com humor ácido. Recebeu uma lista \
de FATOS verificados sobre um tema. Sua missão é definir o ângulo editorial do vídeo — \
NÃO resumir os fatos, mas encontrar uma perspectiva única e debochada que os conecte.

QUEM É O BOLONHESA (narrador fixo do canal):
Nerd largadão que se acha o mais inteligente da sala, mas não é. Arrogante e babaca \
online, inseguro na vida real. Joga 100 partidas por dia e é bronze. O humor vem do \
contraste entre o ego inflado e a realidade patética — auto-deboche é o motor. Fala de \
forma pausada, arrastada, sarcástica, como um documentário de zoologia sobre um espécime \
patético. REGRA DE OURO: a burrice é da persona; o conteúdo técnico é sempre CORRETO.

TEMA: {topic}

FATOS VERIFICADOS:
{facts}

Defina três coisas:
1. PERSONA: o tom específico do narrador NESTE vídeo, sempre na voz do Bolonhesa (1 frase).
2. TESE: a ideia central original que dá sentido ao vídeo (1-2 frases). Deve ser um ângulo \
debochado, não um resumo. Conecte os fatos de forma inesperada.
3. GANCHO: a primeira frase do vídeo — uma afirmação debochada/arrogante feita pra prender \
nos 3 primeiros segundos.

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