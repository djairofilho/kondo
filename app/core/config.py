from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Kondo API"
    database_url: str = "sqlite:///./kondo.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080,http://127.0.0.1:8080"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    ai_provider: str = "anthropic"
    ai_model: str = "claude-haiku-4-5"
    ai_enable_mock_fallback: bool = True
    ai_timeout_seconds: int = 12
    jwt_secret_key: str = "dev-only-change-me"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

