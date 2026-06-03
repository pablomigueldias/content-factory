import logging
import random

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

STRUCTURES = [
    "Cronológica: conte na ordem em que os fatos acontecem no tempo.",
    "Mistério → revelação: abra com uma pergunta intrigante e só revele a resposta no fim.",
    "Contraste: organize em torno de uma oposição (antes/depois, mito/realidade).",
    "Lista-surpresa: encadeie fatos como descobertas crescentes, da menor à mais surpreendente.",
    "Causa → consequência: parta de um fenômeno e desdobre seus efeitos em cadeia.",
]

SCRIPTING_PROMPT = """Você é um roteirista de um canal de curiosidades estilo Discovery, \
em português do Brasil. Você já tem o ângulo editorial definido e uma lista de fatos \
verificados. Sua missão é escrever o ROTEIRO do vídeo, dividido em CENAS.

ÂNGULO EDITORIAL:
- Persona (tom do narrador): {persona}
- Tese (ideia central): {thesis}
- Gancho (primeira frase): {hook}

ESTRUTURA NARRATIVA OBRIGATÓRIA DESTE VÍDEO:
{structure}

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
- Escreva entre 4 e 10 cenas.
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
    structure = random.choice(STRUCTURES)
    prompt = SCRIPTING_PROMPT.format(
        persona=angle.persona,
        thesis=angle.thesis,
        hook=angle.hook,
        structure=structure,
        facts=facts_text,
    )

    raw = llm.generate_text(prompt)
    script = parse_script(raw)

    db.add_all([
        Scene(
            job_id=job.id,
            position=i,
            narration=scene.narration,
            verdade_tecnica=scene.verdade_tecnica,
            visual_description=scene.visual_description,
            duration_seconds=scene.duration_seconds,
        )
        for i, scene in enumerate(script.scenes)
    ])
    db.flush()

    logger.info("Roteiro gerado para job %s: %d cenas (estrutura=%r).",
                job.id, len(script.scenes), structure[:30])