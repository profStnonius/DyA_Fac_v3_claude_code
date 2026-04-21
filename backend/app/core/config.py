from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    APP_NAME: str = "CFDI Intelligence Platform"
    APP_ENV: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    # Database
    DATABASE_URL: str  # postgresql+asyncpg://user:pass@host:port/dbname

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str = "http://localhost:3000/callback"

    # Object Storage (S3-compatible / MinIO)
    STORAGE_ENDPOINT_URL: str = "http://localhost:9000"
    STORAGE_ACCESS_KEY: str
    STORAGE_SECRET_KEY: str
    STORAGE_REGION: str = "us-east-1"
    STORAGE_BUCKET_RAW: str = "raw-email-attachments"
    STORAGE_BUCKET_CFDI: str = "normalized-cfdi"
    STORAGE_BUCKET_UPLOADS: str = "zip-uploads"
    STORAGE_BUCKET_REPORTS: str = "generated-reports"
    STORAGE_BUCKET_TEMP: str = "temp-processing"

    # JWT
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Token encryption (Fernet key, base64)
    FERNET_KEY: str

    # Celery task limits
    CELERY_TASK_SOFT_TIME_LIMIT: int = 300
    CELERY_TASK_TIME_LIMIT: int = 600


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
