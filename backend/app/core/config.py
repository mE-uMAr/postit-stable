"""Application settings, loaded from environment / .env (pydantic-settings)."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ---- App ----
    PROJECT_NAME: str = "Postit API"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me"
    LOG_LEVEL: str = "INFO"

    # ---- Database ----
    DATABASE_URL: str = "sqlite+aiosqlite:///./postit.db"
    SQL_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 1800

    # ---- Redis ----
    REDIS_URL: str | None = None

    # ---- Auth ----
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_TTL_MINUTES: int = 30
    REFRESH_TOKEN_TTL_DAYS: int = 30
    TOKEN_ENCRYPTION_KEY: str | None = None

    # ---- CORS / frontend ----
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    # ---- Rate limiting ----
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 120

    # ---- Stripe ----
    STRIPE_SECRET_KEY: str | None = None
    STRIPE_PUBLISHABLE_KEY: str | None = None
    STRIPE_WEBHOOK_SECRET: str | None = None
    STRIPE_CURRENCY: str = "usd"

    # ---- Seed ----
    SEED_SUPERADMIN_EMAIL: str = "admin@postit.app"
    SEED_SUPERADMIN_PASSWORD: str = "admin12345"
    SEED_DEMO_EMAIL: str = "rina@maple.co"
    SEED_DEMO_PASSWORD: str = "password123"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors(cls, v: object) -> object:
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def stripe_enabled(self) -> bool:
        return bool(self.STRIPE_SECRET_KEY and not self.STRIPE_SECRET_KEY.endswith("REPLACE_ME"))


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
