# interface/config.py

from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """
    Application settings.

    Loaded from environment variables and .env file.

    Thread-safe singleton via get_settings().
    """

    APP_ENV: str = "development"

    DATABASE_URL: str

    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # ✅ Pydantic v2 correct configuration
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Settings singleton.

    Guarantees:
    - single instance per process
    - thread-safe
    - fast access
    """
    return Settings()