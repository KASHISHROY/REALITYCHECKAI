from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RealityCheck AI"
    app_version: str = "0.1.0"
    app_env: str = "development"
    database_url: str = "sqlite:///./realitycheck.db"
    repo_storage_path: str = "storage/repos"
    cors_origins: list[str] = ["http://localhost:5173"]
    groq_api_key: str | None = None
    openai_api_key: str | None = None
    groq_model: str = "llama-3.1-8b-instant"
    openai_model: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
