import pytest

from app.schemas.scene import parse_script

VALID = '{"scenes": [{"narration": "Olá", "visual_description": "Céu azul", "duration_seconds": 8}]}'


def test_parse_valid_script():
    script = parse_script(VALID)
    assert len(script.scenes) == 1
    assert script.scenes[0].narration == "Olá"
    assert script.scenes[0].duration_seconds == 8


def test_parse_strips_markdown_fence():
    script = parse_script(f"```json\n{VALID}\n```")
    assert len(script.scenes) == 1


def test_parse_trims_whitespace_in_text():
    raw = '{"scenes": [{"narration": "  oi  ", "visual_description": "x", "duration_seconds": 5}]}'
    assert parse_script(raw).scenes[0].narration == "oi"


def test_parse_empty_scenes_raises():
    with pytest.raises(ValueError):
        parse_script('{"scenes": []}')


def test_parse_blank_narration_raises():
    raw = '{"scenes": [{"narration": "   ", "visual_description": "x", "duration_seconds": 5}]}'
    with pytest.raises(ValueError):
        parse_script(raw)


def test_parse_duration_out_of_bounds_raises():
    raw = '{"scenes": [{"narration": "n", "visual_description": "v", "duration_seconds": 999}]}'
    with pytest.raises(ValueError):
        parse_script(raw)


def test_parse_non_json_raises():
    with pytest.raises(ValueError):
        parse_script("isso não é json")