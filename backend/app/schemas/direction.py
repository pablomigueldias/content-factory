import json
from typing import Literal

from pydantic import BaseModel, Field, field_validator

# Conjuntos fechados — validados por Pydantic, não por Enum no banco (ver Passo 2).
CameraMovement = Literal[
    "static", "zoom_in", "zoom_out", "pan_left", "pan_right",
    "tilt_up", "tilt_down", "tracking",
]
CameraIntensity = Literal["subtle", "medium", "aggressive"]
Framing = Literal["close_up", "medium_shot", "wide_shot", "extreme_close_up"]
GazeDirection = Literal["to_camera", "away", "up_thinking", "side_eye"]
Transition = Literal["hard_cut", "crossfade", "whip_pan", "zoom_transition", "glitch"]
CutSpeed = Literal["slow", "medium", "fast"]


class CutPlan(BaseModel):
    transition_in: Transition
    transition_out: Transition
    cut_speed: CutSpeed
    impact_moment_seconds: float | None = None
    notes: str | None = None


class Pause(BaseModel):
    after_word: str
    duration_ms: int = Field(ge=0)


class NarrationCues(BaseModel):
    pauses: list[Pause] = Field(default_factory=list)
    emphasis: list[str] = Field(default_factory=list)
    tone: str | None = None


class SceneDirection(BaseModel):
    """Direção criativa de UMA cena, alinhada por `position` à `Scene`.

    Os slugs de expressão/pose são `str` (não Literal) porque o conjunto válido
    vem do manifest.json, que muda; quem valida contra o manifesto é o orquestrador.
    """
    position: int = Field(ge=0)
    storyboard: str
    camera_movement: CameraMovement
    camera_intensity: CameraIntensity
    framing: Framing
    expression_slug: str
    pose_slug: str
    gaze_direction: GazeDirection
    emotion: str
    image_prompt: str
    animation_prompt: str
    cut_plan: CutPlan
    narration_cues: NarrationCues

    @field_validator(
        "storyboard", "expression_slug", "pose_slug",
        "emotion", "image_prompt", "animation_prompt",
    )
    @classmethod
    def _not_blank(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("campo de texto não pode ser vazio")
        return cleaned


class DirectionPlan(BaseModel):
    """Direção completa retornada pelo LLM, uma entrada por cena."""
    scenes: list[SceneDirection] = Field(min_length=1)


def parse_direction(raw: str) -> DirectionPlan:
    cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    data = json.loads(cleaned)
    return DirectionPlan.model_validate(data)
