import pytest
from pydantic import ValidationError

from app.schemas.direction import parse_direction

VALID = (
    '{"scenes": [{'
    '"position": 0, "storyboard": "encara a câmera e revira os olhos", '
    '"camera_movement": "zoom_in", "camera_intensity": "aggressive", '
    '"framing": "close_up", "expression_slug": "deboche", '
    '"pose_slug": "bracos-cruzados", "gaze_direction": "to_camera", '
    '"emotion": "deboche crescente", "image_prompt": "flat 2D cartoon...", '
    '"animation_prompt": "zoom in agressivo", '
    '"cut_plan": {"transition_in": "hard_cut", "transition_out": "whip_pan", '
    '"cut_speed": "fast", "impact_moment_seconds": 2.4, "notes": "corte seco"}, '
    '"narration_cues": {"pauses": [{"after_word": "framework", "duration_ms": 400}], '
    '"emphasis": ["rápido"], "tone": "debochado_crescente"}'
    '}]}'
)


def test_parse_valid_direction():
    plan = parse_direction(VALID)
    d = plan.scenes[0]
    assert d.position == 0
    assert d.camera_movement == "zoom_in"
    assert d.cut_plan.transition_out == "whip_pan"
    assert d.cut_plan.impact_moment_seconds == 2.4
    assert d.narration_cues.emphasis == ["rápido"]
    assert d.narration_cues.pauses[0].duration_ms == 400


def test_parse_strips_markdown_fence():
    plan = parse_direction("```json\n" + VALID + "\n```")
    assert plan.scenes[0].framing == "close_up"


def test_invalid_enum_value_rejected():
    bad = VALID.replace('"camera_movement": "zoom_in"', '"camera_movement": "flip"')
    with pytest.raises(ValidationError):
        parse_direction(bad)


def test_blank_text_field_rejected():
    bad = VALID.replace('"storyboard": "encara a câmera e revira os olhos"',
                        '"storyboard": "   "')
    with pytest.raises(ValidationError):
        parse_direction(bad)


def test_empty_scenes_rejected():
    with pytest.raises(ValidationError):
        parse_direction('{"scenes": []}')
