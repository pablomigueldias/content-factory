import logging

from google import genai

from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiProvider:

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_model
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY não configurada no .env")
        self._client = genai.Client(api_key=self.api_key)

    def generate_text(self, prompt: str) -> str:
        response = self._client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return (response.text or "").strip()