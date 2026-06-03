import logging

from sqlalchemy.orm import Session

from app.models.editorial import EditorialAngle
from app.models.fact import Fact
from app.models.scene import Scene
from app.models.source import Source
from app.models.video_job import VideoJob
from app.providers.gemini_client import GeminiProvider
from app.providers.llm import LLMProvider
from app.schemas.scene import parse_script

logger = logging.getLogger(__name__)

SCRIPTING_PROMPT = """Você é o roteirista do canal do GORDÃO BOLONHESA, um short de TI \
em português do Brasil com humor ácido. Você já tem o ângulo editorial definido e uma \
lista de fatos verificados. Sua missão é escrever o ROTEIRO do vídeo, dividido em CENAS.

ÂNGULO EDITORIAL:
- Persona (tom do narrador): {persona}
- Tese (ideia central): {thesis}
- Gancho (primeira frase): {hook}

FÓRMULA OBRIGATÓRIA (4 batidas de um short de 30-60s):
1. GANCHO (primeira cena, ~0-3s): afirmação debochada que cria tensão e prende.
2. DENSIDADE (cenas do meio): fato + ironia em CADA cena, ritmo de metralhadora, \
uma tirada ácida a cada cena. Técnico sempre correto.
3. AHÁ (penúltima cena): a virada onde o espectador APRENDE algo de verdade.
4. RETENÇÃO (última cena): uma ponta solta/provocação que puxa pro próximo vídeo \
(sem venda, sem "se inscreva").

FATOS VERIFICADOS (use apenas estes; não invente):
{facts}

Cada cena é dividida em DUAS camadas de narração:
- "bravata": a atitude debochada e arrogante do narrador — ego inflado, deboche, \
auto-confiança patética. É o humor. Pode estar errada de ATITUDE, nunca de fato.
- "verdade_tecnica": a informação CORRETA de verdade, sem invenção. É o que o \
espectador aprende. Tem que estar tecnicamente certa, baseada nos fatos verificados.
O áudio falado será a bravata seguida da verdade técnica, então as duas camadas \
devem encaixar como uma fala contínua.

Regras:
- A primeira cena DEVE começar (na bravata) com o gancho.
- Cada cena tem: bravata, verdade_tecnica, descrição visual (o que aparece na tela) \
e duração em segundos (entre 2 e 60).
- Escreva entre 4 e 6 cenas, somando ~30-60s no total (é um short).
- A narração deve fluir como texto falado contínuo entre as cenas, não tópicos soltos.
- Respeite o tom da persona na bravata; mantenha a verdade_tecnica precisa.

Responda APENAS com JSON no formato EXATO:
{{"scenes": [{{"bravata": "...", "verdade_tecnica": "...", "visual_description": "...", "duration_seconds": 8}}]}}
"""


def run_scripting(job: VideoJob, db: Session, llm: LLMProvider | None = None) -> None:
    llm = llm or GeminiProvider()

    angle = db.query(EditorialAngle).filter_by(job_id=job.id).one_or_none()
    if angle is None:
        raise ValueError(f"Sem ângulo editorial para gerar roteiro (job {job.id})")

    facts = (
        db.query(Fact)
        .join(Source, Fact.source_id == Source.id)
        .filter(Source.job_id == job.id)
        .all()
    )
    if not facts:
        raise ValueError(f"Sem fatos para gerar roteiro (job {job.id})")

    facts_text = "\n".join(f"- {f.content}" for f in facts)
    prompt = SCRIPTING_PROMPT.format(
        persona=angle.persona,
        thesis=angle.thesis,
        hook=angle.hook,
        facts=facts_text,
    )

    raw = llm.generate_text(prompt)
    script = parse_script(raw)

    db.add_all([
        Scene(
            job_id=job.id,
            position=i,
            narration=scene.narration,
            bravata=scene.bravata,
            verdade_tecnica=scene.verdade_tecnica,
            visual_description=scene.visual_description,
            duration_seconds=scene.duration_seconds,
        )
        for i, scene in enumerate(script.scenes)
    ])
    db.flush()

    logger.info("Roteiro gerado para job %s: %d cenas.", job.id, len(script.scenes))