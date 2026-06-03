from typing import Protocol


class TTSProvider(Protocol):
    def synthesize(self, text: str, out_path: str) -> None:
        """Gera um WAV em out_path a partir do texto."""
        ...

    def unload(self) -> None:
        """Libera o modelo da VRAM (chamado ao fim da etapa)."""
        ...