import gc
import logging

from app.core.config import settings
from app.core.gpu import gpu_lock

logger = logging.getLogger(__name__)


def _resolve_device(configured: str) -> str:
    if configured:
        return configured
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
        if torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass
    return "cpu"


class ChatterboxProvider:
    def __init__(self, device: str | None = None, language: str | None = None,
                 voice_reference: str | None = None,
                 exaggeration: float | None = None, cfg_weight: float | None = None,
                 temperature: float | None = None):
        self.device = _resolve_device(
            device if device is not None else settings.tts_model_device
        )
        self.language = language or settings.tts_language
        self.voice_reference = (
            voice_reference if voice_reference is not None else settings.tts_voice_reference
        )
        self.exaggeration = (
            exaggeration if exaggeration is not None else settings.tts_exaggeration
        )
        self.cfg_weight = (
            cfg_weight if cfg_weight is not None else settings.tts_cfg_weight
        )
        self.temperature = (
            temperature if temperature is not None else settings.tts_temperature
        )
        self._model = None

    def _generate_kwargs(self) -> dict:
        kwargs = {
            "language_id": self.language,
            "exaggeration": self.exaggeration,
            "cfg_weight": self.cfg_weight,
            "temperature": self.temperature,
        }
        if self.voice_reference:
            kwargs["audio_prompt_path"] = self.voice_reference
        return kwargs

    def _ensure_model(self):
        if self._model is None:
            from chatterbox.mtl_tts import ChatterboxMultilingualTTS 
            logger.info("Carregando Chatterbox multilingual em %s...", self.device)
            self._model = ChatterboxMultilingualTTS.from_pretrained(device=self.device) #type: ignore
        return self._model

    def synthesize(self, text: str, out_path: str) -> None:
        import torchaudio as ta

        model = self._ensure_model()
        kwargs = self._generate_kwargs()

        with gpu_lock("chatterbox"):
            wav = model.generate(text, **kwargs)  #type: ignore
        ta.save(out_path, wav, model.sr)
        logger.debug("Áudio gerado: %s", out_path)

    def unload(self) -> None:
        if self._model is None:
            return
        self._model = None
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass
        logger.info("Chatterbox descarregado da memória.")