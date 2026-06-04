"""Lê o manifest.json da biblioteca do personagem.

Fonte única de verdade para os slugs válidos de expressão e pose, mais os tokens
de estilo que todo prompt de imagem deve repetir. A direção criativa valida os
slugs do LLM contra esta lista; o export resolve os caminhos dos arquivos.
"""
import json
from dataclasses import dataclass
from pathlib import Path

from app.core.config import settings


@dataclass(frozen=True)
class CharacterLibrary:
    name: str
    style: str
    manifest_dir: Path
    expressions: dict[str, str]  # slug -> caminho do arquivo (relativo ao manifesto)
    poses: dict[str, str]        # slug -> caminho do arquivo (relativo ao manifesto)
    emotions: dict[str, str]     # slug de expressão -> rótulo de emoção

    @property
    def expression_slugs(self) -> list[str]:
        return list(self.expressions)

    @property
    def pose_slugs(self) -> list[str]:
        return list(self.poses)

    def expression_path(self, slug: str) -> Path | None:
        """Caminho absoluto do PNG da expressão, ou None se o slug não existe."""
        rel = self.expressions.get(slug)
        return self.manifest_dir / rel if rel else None

    def pose_path(self, slug: str) -> Path | None:
        rel = self.poses.get(slug)
        return self.manifest_dir / rel if rel else None


def load_character_library(manifest_path: str | Path | None = None) -> CharacterLibrary:
    path = Path(manifest_path or settings.character_manifest_path)
    if not path.exists():
        raise FileNotFoundError(f"Manifesto do personagem não encontrado em {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    expressions = {e["slug"]: e["arquivo"] for e in data.get("expressoes", [])}
    emotions = {e["slug"]: e.get("emocao", "") for e in data.get("expressoes", [])}
    poses = {p["slug"]: p["arquivo"] for p in data.get("poses", [])}

    return CharacterLibrary(
        name=data.get("personagem", ""),
        style=data.get("estilo", ""),
        manifest_dir=path.parent,
        expressions=expressions,
        poses=poses,
        emotions=emotions,
    )
