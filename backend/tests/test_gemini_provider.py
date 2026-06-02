from app.providers.gemini_client import GeminiProvider


class _FakeResponse:
    text = "  resposta gerada  "


class _FakeModels:
    def generate_content(self, model, contents):
        return _FakeResponse()


def test_generate_text_strips_and_returns(monkeypatch):
    provider = GeminiProvider.__new__(GeminiProvider)  # pula o __init__ (sem key real)
    provider.model = "gemini-2.5-flash"

    class _FakeClient:
        models = _FakeModels()

    provider._client = _FakeClient() #type: ignore

    assert provider.generate_text("qualquer prompt") == "resposta gerada"


def test_init_without_key_raises(monkeypatch):
    monkeypatch.setattr("app.providers.gemini_client.settings.gemini_api_key", "")
    import pytest
    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        GeminiProvider(api_key="")