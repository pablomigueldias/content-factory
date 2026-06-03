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


def test_generate_kwargs_carries_tone_params_without_reference():
    provider = ChatterboxProvider(
        device="cpu", language="pt",
        exaggeration=0.7, cfg_weight=0.3, temperature=0.9,
    )
    kwargs = provider._generate_kwargs()
    assert kwargs == {
        "language_id": "pt",
        "exaggeration": 0.7,
        "cfg_weight": 0.3,
        "temperature": 0.9,
    }
    assert "audio_prompt_path" not in kwargs


def test_generate_kwargs_adds_voice_reference_when_set():
    provider = ChatterboxProvider(device="cpu", voice_reference="ref/bolonhesa.wav")
    assert provider._generate_kwargs()["audio_prompt_path"] == "ref/bolonhesa.wav"