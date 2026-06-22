"""Settings de la app. Carga desde .env."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # API keys
    spotify_client_id: str = ""
    spotify_client_secret: str = ""
    lastfm_api_key: str = ""
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # App
    app_env: str = "dev"
    log_level: str = "INFO"

    # JWT
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    session_ttl_minutes: int = 30

    # Storage
    database_url: str = "sqlite+aiosqlite:///./nyota.db"
    redis_url: str = "memory://"

    @property
    def use_fakeredis(self) -> bool:
        return self.redis_url.startswith("memory://")


@lru_cache
def get_settings() -> Settings:
    return Settings()
