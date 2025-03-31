import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import Optional

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)


class Settings(BaseSettings):
    PROJECT_NAME: str = "Crypto API"
    API_V1_STR: str = "/api/v1"

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    DATABASE_URL: Optional[str] = None

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    COINGECKO_API_BASE_URL: str = "https://api.coingecko.com/api/v3"

    class Config:
        case_sensitive = True


settings = Settings()