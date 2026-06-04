import logging

from sqlalchemy.orm import Session

from app.models.editorial import EditorialAngle
from app.models.scene import Scene
from app.models.video_job import VideoJob
from app.providers.character_library import CharacterLibrary, load_character_library
from app.providers.gemini_client import GeminiProvider
from app.providers.llm import LLMProvider
from app.schemas.direction import SceneDirection, parse_direction

logger = logging.getLogger(__name__)

_FALLBACK_EXPRESSION = "neutro"

DIRECTION_PROMPT = """Você é o DIRETOR do canal do GORDÃO BOLONHESA, um short de TI em \
português do Brasil com humor ácido. O roteiro já está escrito e dividido em cenas. \
Sua missão é DIRIGIR cada cena: enquadramento, câmera, expressão/pose do personagem, \
prompts de imagem e de animação, e plano de corte — tudo otimizado para RETENÇÃO.

ÂNGULO EDITORIAL (tom que rege a direção):
- Persona (tom do narrador): {persona}
- Tese (ideia central): {thesis}
- Gancho (primeira frase): {hook}

ESTILO VISUAL OBRIGATÓRIO (repita SEMPRE no image_prompt, palavra por palavra):
"{style}"
O personagem é "{character}". Todo image_prompt deve descrever o MESMO rosto, roupa e \
estilo entre as cenas, pra não quebrar a consistência do personagem.

EXPRESSÕES DISPONÍVEIS (use o slug exato; nenhum outro existe):
{expressions}

POSES DISPONÍVEIS (use o slug exato; nenhuma outra existe):
{poses}

REGRAS DE DIREÇÃO:
- A camada "bravata" carrega o ego/deboche; escolha a expressão que vende a atitude \
(ex.: deboche, olhos-revirados, rindo). A "verdade_tecnica" carrega a explicação/ \
autoridade (ex.: nerd, pensativo, eureka). Deixe a expressão servir à camada que pesa na cena.
- camera_movement serve ao ritmo: zoom_in cresce tensão no gancho (cena 0); \
hard_cut + whip_pan aceleram a densidade do meio; um respiro (static) na batida Ahá.
- Otimize os 3 primeiros segundos (o gancho) e a última cena (ponta solta/retenção).
- camera_movement ∈ static, zoom_in, zoom_out, pan_left, pan_right, tilt_up, tilt_down, tracking.
- camera_intensity ∈ subtle, medium, aggressive.
- framing ∈ close_up, medium_shot, wide_shot, extreme_close_up.
- gaze_direction ∈ to_camera, away, up_thinking, side_eye.
- cut_plan.transition_in / transition_out ∈ hard_cut, crossfade, whip_pan, zoom_transition, glitch.
- cut_plan.cut_speed ∈ slow, medium, fast.

CENAS DO ROTEIRO (dirija TODAS, mantendo o mesmo `position`):
{scenes}

Responda APENAS com JSON no formato EXATO (uma entrada por cena, na mesma ordem):
{{"scenes": [{{"position": 0, "storyboard": "...", "camera_movement": "zoom_in", \
"camera_intensity": "medium", "framing": "close_up", "expression_slug": "deboche", \
"pose_slug": "bracos-cruzados", "gaze_direction": "to_camera", "emotion": "deboche crescente", \
"image_prompt": "...", "animation_prompt": "...", \
"cut_plan": {{"transition_in": "hard_cut", "transition_out": "whip_pan", \
"cut_speed": "fast", "impact_moment_seconds": 2.4, "notes": "..."}}, \
"narration_cues": {{"pauses": [{{"after_word": "framework", "duration_ms": 400}}], \
"emphasis": ["rápido"], "tone": "debochado_crescente"}}}}]}}
"""


def _format_scenes(scenes: list[Scene]) -> str:
    lines = []
    for s in scenes:
        lines.append(
            f"- position {s.position} ({s.duration_seconds}s)\n"
            f"  bravata: {s.bravata or ''}\n"
            f"  verdade_tecnica: {s.verdade_tecnica or ''}"
        )
    return "\n".join(lines)


def _apply_direction(
    scene: Scene, direction: SceneDirection, library: CharacterLibrary
) -> str | None:
    """Preenche os campos de direção na cena. Retorna o motivo de revisão, se houver."""
    review_reason = None
    expression = direction.expression_slug
    pose = direction.pose_slug

    bad = []
    if expression not in library.expressions:
        bad.append(f"expressão '{expression}'")
        expression = _FALLBACK_EXPRESSION if _FALLBACK_EXPRESSION in library.expressions else None
    if pose not in library.poses:
        bad.append(f"pose '{pose}'")
        pose = None
    if bad:
        review_reason = "Slug inválido fora do manifesto: " + ", ".join(bad)

    scene.storyboard = direction.storyboard
    scene.camera_movement = direction.camera_movement
    scene.camera_intensity = direction.camera_intensity
    scene.framing = direction.framing
    scene.expression_slug = expression
    scene.pose_slug = pose
    scene.gaze_direction = direction.gaze_direction
    scene.emotion = direction.emotion
    scene.image_prompt = direction.image_prompt
    scene.animation_prompt = direction.animation_prompt
    scene.cut_plan = direction.cut_plan.model_dump()
    scene.narration_cues = direction.narration_cues.model_dump()
    return review_reason


def run_direction(job: VideoJob, db: Session, llm: LLMProvider | None = None) -> None:
    llm = llm or GeminiProvider()

    scenes = (
        db.query(Scene).filter_by(job_id=job.id).order_by(Scene.position).all()
    )
    if not scenes:
        raise ValueError(f"Sem cenas para dirigir (job {job.id})")

    angle = db.query(EditorialAngle).filter_by(job_id=job.id).one_or_none()
    if angle is None:
        raise ValueError(f"Sem ângulo editorial para dirigir (job {job.id})")

    library = load_character_library()

    expressions_text = "\n".join(
        f"- {slug} (emoção: {library.emotions.get(slug, '')})"
        for slug in library.expression_slugs
    )
    poses_text = "\n".join(f"- {slug}" for slug in library.pose_slugs)
    prompt = DIRECTION_PROMPT.format(
        persona=angle.persona,
        thesis=angle.thesis,
        hook=angle.hook,
        style=library.style,
        character=library.name,
        expressions=expressions_text,
        poses=poses_text,
        scenes=_format_scenes(scenes),
    )

    raw = llm.generate_text(prompt)
    plan = parse_direction(raw)
    by_position = {d.position: d for d in plan.scenes}

    flagged = 0
    for scene in scenes:
        direction = by_position.get(scene.position)
        if direction is None:
            scene.needs_review = True
            scene.review_reason = "Sem direção criativa gerada para esta cena"
            flagged += 1
            continue

        reason = _apply_direction(scene, direction, library)
        if reason is not None:
            scene.needs_review = True
            scene.review_reason = reason
            flagged += 1

    db.flush()

    logger.info(
        "Direção criativa do job %s: %d cenas dirigidas, %d sinalizadas p/ revisão.",
        job.id, len(scenes), flagged,
    )
