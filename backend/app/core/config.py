from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Content Factory"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://factory:factory@localhost:5435/content_factory"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"


    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()