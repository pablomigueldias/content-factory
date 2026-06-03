from app.providers.chatterbox_tts import ChatterboxProvider, _resolve_device


def test_resolve_device_respects_explicit_config():
    assert _resolve_device("cpu") == "cpu"
    assert _resolve_device("cuda") == "cuda"


def test_provider_does_not_load_model_on_init():
    provider = ChatterboxProvider(device="cpu")
    assert provider._model is None


def test_unload_is_safe_without_loaded_model():
    provider = ChatterboxProvider(device="cpu")
    provider.unload()
    assert provider._model is None