import json

import pytest

from app.providers.character_library import load_character_library

MANIFEST = {
    "personagem": "Nerd Bolonhesa",
    "estilo": "flat 2D cartoon, contorno grosso, cores chapadas",
    "ancora": "ancora/x.png",
    "expressoes": [
        {"slug": "neutro", "emocao": "neutro", "arquivo": "expressoes/neutro.png"},
        {"slug": "deboche", "emocao": "sarcasmo", "arquivo": "expressoes/deboche.png"},
    ],
    "poses": [
        {"slug": "apontando", "arquivo": "poses/apontando.png"},
    ],
}


def _write_manifest(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(MANIFEST), encoding="utf-8")
    return path


def test_load_lists_slugs_and_style(tmp_path):
    lib = load_character_library(_write_manifest(tmp_path))
    assert lib.name == "Nerd Bolonhesa"
    assert lib.style.startswith("flat 2D cartoon")
    assert lib.expression_slugs == ["neutro", "deboche"]
    assert lib.pose_slugs == ["apontando"]
    assert lib.emotions["deboche"] == "sarcasmo"


def test_resolves_file_paths_relative_to_manifest(tmp_path):
    lib = load_character_library(_write_manifest(tmp_path))
    assert lib.expression_path("deboche") == tmp_path / "expressoes/deboche.png"
    assert lib.pose_path("apontando") == tmp_path / "poses/apontando.png"
    assert lib.expression_path("nao-existe") is None
    assert lib.pose_path("nao-existe") is None


def test_missing_manifest_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_character_library(tmp_path / "ausente.json")


def test_real_manifest_loads():
    """A biblioteca real do Bolonhesa carrega e tem os slugs esperados."""
    lib = load_character_library()
    assert "neutro" in lib.expression_slugs
    assert lib.pose_slugs
    assert lib.style
