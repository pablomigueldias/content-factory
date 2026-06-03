from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Content Factory"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://factory:factory@localhost:5435/content_factory"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    media_root: str = "media"

    tts_model_device: str = ""
    tts_language: str = "pt"
    tts_voice_reference: str = ""
    # Tom da voz (entonação debochada do Bolonhesa). Defaults = defaults do Chatterbox;
    # menor cfg_weight = fala mais lenta/arrastada. Calibrar via .env na Fase 1.
    tts_exaggeration: float = 0.5
    tts_cfg_weight: float = 0.5
    tts_temperature: float = 0.8

    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    reranker_device: str = ""
    factcheck_threshold: float = 0.5

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
