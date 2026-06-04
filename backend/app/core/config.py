"""Application settings, loaded from environment / .env (pydantic-settings)."""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


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
    PASSWORD_RESET_TTL_MINUTES: int = 30
    TOKEN_ENCRYPTION_KEY: str | None = None

    # ---- CORS / frontend ----
    FRONTEND_URL: str = "http://localhost:3000"
    # NoDecode: keep pydantic-settings from JSON-parsing the raw env value so
    # the validator below can accept a plain comma-separated string (or "*").
    CORS_ORIGINS: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )

    # ---- Rate limiting ----
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 120

    # ---- Scheduler / publish worker ----
    SCHEDULER_ENABLED: bool = True          # run the in-process publish worker
    SCHEDULER_POLL_SECONDS: int = 10        # how often to drain the outbox
    SCHEDULER_MAX_ATTEMPTS: int = 3         # retries before a job is marked failed

    # ---- AI provider (pluggable; see app/services/ai) ----
    AI_ENABLED: bool = True                 # master switch; mock is used when off/unconfigured
    AI_PROVIDER: str = "mock"               # mock | anthropic | openai | groq | gemini
    AI_API_KEY: str | None = None
    AI_MODEL: str | None = None             # provider-specific default applied when unset
    AI_BASE_URL: str | None = None          # override for self-hosted / OpenAI-compatible gateways
    AI_TIMEOUT_SECONDS: float = 30.0
    AI_MAX_TOKENS: int = 600

    # ---- Paddle (Billing) ----
    PADDLE_API_KEY: str | None = None          # server-side secret key
    PADDLE_CLIENT_TOKEN: str | None = None     # public client-side token (Paddle.js)
    PADDLE_WEBHOOK_SECRET: str | None = None
    PADDLE_ENVIRONMENT: str = "sandbox"        # sandbox | production
    PADDLE_CURRENCY: str = "USD"

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
    def paddle_enabled(self) -> bool:
        return bool(self.PADDLE_API_KEY and not self.PADDLE_API_KEY.endswith("REPLACE_ME"))

    @property
    def paddle_api_base(self) -> str:
        return (
            "https://api.paddle.com"
            if self.PADDLE_ENVIRONMENT.lower() == "production"
            else "https://sandbox-api.paddle.com"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
