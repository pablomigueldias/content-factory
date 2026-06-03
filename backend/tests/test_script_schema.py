import pytest

from app.schemas.scene import parse_script

VALID = (
    '{"scenes": [{'
    '"bravata": "Óbvio que eu domino async, sou dev raiz",'
    '"verdade_tecnica": "await suspende a corrotina e devolve o controle ao event loop",'
    '"visual_description": "Código com await destacado",'
    '"duration_seconds": 8}]}'
)


def test_parse_valid_script():
    script = parse_script(VALID)
    assert len(script.scenes) == 1
    scene = script.scenes[0]
    assert scene.bravata == "Óbvio que eu domino async, sou dev raiz"
    assert scene.verdade_tecnica.startswith("await suspende")
    assert scene.duration_seconds == 8


def test_narration_concatenates_bravata_then_truth():
    scene = parse_script(VALID).scenes[0]
    assert scene.narration == (
        "Óbvio que eu domino async, sou dev raiz "
        "await suspende a corrotina e devolve o controle ao event loop"
    )


def test_parse_strips_markdown_fence():
    script = parse_script(f"```json\n{VALID}\n```")
    assert len(script.scenes) == 1


def test_parse_trims_whitespace_in_layers():
    raw = (
        '{"scenes": [{"bravata": "  ego  ", "verdade_tecnica": "  fato  ",'
        ' "visual_description": "x", "duration_seconds": 5}]}'
    )
    scene = parse_script(raw).scenes[0]
    assert scene.bravata == "ego"
    assert scene.verdade_tecnica == "fato"
    assert scene.narration == "ego fato"


def test_parse_empty_scenes_raises():
    with pytest.raises(ValueError):
        parse_script('{"scenes": []}')


def test_parse_blank_bravata_raises():
    raw = ('{"scenes": [{"bravata": "   ", "verdade_tecnica": "fato",'
           ' "visual_description": "x", "duration_seconds": 5}]}')
    with pytest.raises(ValueError):
        parse_script(raw)


def test_parse_blank_verdade_raises():
    raw = ('{"scenes": [{"bravata": "ego", "verdade_tecnica": "   ",'
           ' "visual_description": "x", "duration_seconds": 5}]}')
    with pytest.raises(ValueError):
        parse_script(raw)


def test_parse_missing_layer_raises():
    raw = ('{"scenes": [{"bravata": "ego",'
           ' "visual_description": "x", "duration_seconds": 5}]}')
    with pytest.raises(ValueError):
        parse_script(raw)


def test_parse_duration_out_of_bounds_raises():
    raw = ('{"scenes": [{"bravata": "e", "verdade_tecnica": "v",'
           ' "visual_description": "x", "duration_seconds": 999}]}')
    with pytest.raises(ValueError):
        parse_script(raw)


def test_parse_non_json_raises():
    with pytest.raises(ValueError):
        parse_script("isso não é json")