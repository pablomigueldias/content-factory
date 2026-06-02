import json

from pydantic import BaseModel, Field, field_validator


class SceneDraft(BaseModel):
    narration: str
    visual_description: str
    duration_seconds: int = Field(ge=2, le=60)

    @field_validator("narration", "visual_description")
    @classmethod
    def _not_blank(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("campo de texto não pode ser vazio")
        return cleaned


class ScriptDraft(BaseModel):
    """Roteiro completo retornado pelo LLM."""
    scenes: list[SceneDraft] = Field(min_length=1)


def parse_script(raw: str) -> ScriptDraft:
    cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    data = json.loads(cleaned)          
    return ScriptDraft.model_validate(data)