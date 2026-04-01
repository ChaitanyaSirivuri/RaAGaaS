from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str
    weaviate_url: str = "http://localhost:8080"
    openai_api_key: str = ""
    secret_key: str = "change-me"

    vector_provider: str = "weaviate"
    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"

    chunking_strategy: str = "fixed"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()
