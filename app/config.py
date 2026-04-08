from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App
    APP_NAME: str = "SpeakOps Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API Security
    API_KEY: str
    API_KEY_NAME: str = "X-API-Key"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    CACHE_TTL: int = 60  # seconds

    # Database
    DATABASE_URL: str

    # AI
    AI_MODEL: str = "mock"          # "mock" | "openai" | "custom"
    OPENAI_API_KEY: str = ""

    # Rate limiting
    RATE_LIMIT: str = "100/minute"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()