import os
from pydantic import PostgresDsn, RedisDsn, field_validator, computed_field

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Basic API config
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Cryptocurrency API"

    # DB connection
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "crypto_db")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))

    # Redis connection
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))

    # Coingecko API
    COINGECKO_API_BASE_URL: str = "https://api.coingecko.com/api/v3"

    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

    @computed_field
    @property
    def DATABASE_URI(self) -> PostgresDsn:
        """
        Creates an URI for DB connection.
        """
        return PostgresDsn.build(
            scheme="postgresql",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB
        )

    @computed_field
    @property
    def REDIS_URI(self) -> RedisDsn:
        """
        Creates an URI for Redis connection.
        """
        return RedisDsn.build(
            scheme="redis",
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            path="/0"
        )

    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }


settings = Settings()
