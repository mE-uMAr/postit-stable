"""Application settings, loaded from environment / .env (pydantic-settings)."""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

# Every platform Postit can connect to. Drives the OAuth credential lookup and the
# redirect / deauthorize / delete callback URLs exposed to each provider console.
OAUTH_PLATFORMS: tuple[str, ...] = (
    "x",
    "linkedin",
    "instagram",
    "threads",
    "facebook",
    "tiktok",
    "youtube",
    "wordpress",
    "blogger",
)


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
    # TLS for MySQL. None = auto (on for remote hosts, off for localhost). Set a CA
    # bundle path to additionally verify the server cert (ssl-mode=VERIFY_CA).
    DB_SSL: bool | None = None
    DB_SSL_CA: str | None = None

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

    # ---- Startup bootstrap (deploy) ----
    RUN_MIGRATIONS_ON_STARTUP: bool = False  # run `alembic upgrade head` on boot
    RUN_SEED_ON_STARTUP: bool = False        # run the idempotent core seed on boot

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

    # ---- Email (SMTP) ----
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM: str | None = None            # defaults to SMTP_USER when unset
    SMTP_FROM_NAME: str = "Postit"
    SMTP_USE_TLS: bool = True               # STARTTLS (port 587); for SSL use port 465 + SMTP_USE_SSL
    SMTP_USE_SSL: bool = False

    # ---- Signup OTP (email verification) ----
    OTP_TTL_SECONDS: int = 600
    OTP_LENGTH: int = 6
    OTP_MAX_ATTEMPTS: int = 5

    # ---- Paddle (Billing) ----
    PADDLE_API_KEY: str | None = None          # server-side secret key
    PADDLE_CLIENT_TOKEN: str | None = None     # public client-side token (Paddle.js)
    PADDLE_WEBHOOK_SECRET: str | None = None
    PADDLE_ENVIRONMENT: str = "sandbox"        # sandbox | production
    PADDLE_CURRENCY: str = "USD"

    # ---- Social OAuth (per-platform apps) ----
    # PUBLIC_API_URL is the externally reachable base of this API (no trailing slash).
    # All callback URLs handed to the platform consoles are built from it.
    PUBLIC_API_URL: str = "http://localhost:8000"
    # Shared verify token for the Meta-style webhook GET handshake (Threads/Facebook/Instagram).
    OAUTH_WEBHOOK_VERIFY_TOKEN: str = "change-me-verify-token"

    X_CLIENT_ID: str | None = None
    X_CLIENT_SECRET: str | None = None
    LINKEDIN_CLIENT_ID: str | None = None
    LINKEDIN_CLIENT_SECRET: str | None = None
    INSTAGRAM_CLIENT_ID: str | None = None
    INSTAGRAM_CLIENT_SECRET: str | None = None
    THREADS_CLIENT_ID: str | None = None
    THREADS_CLIENT_SECRET: str | None = None
    FACEBOOK_CLIENT_ID: str | None = None
    FACEBOOK_CLIENT_SECRET: str | None = None
    TIKTOK_CLIENT_ID: str | None = None
    TIKTOK_CLIENT_SECRET: str | None = None
    YOUTUBE_CLIENT_ID: str | None = None
    YOUTUBE_CLIENT_SECRET: str | None = None
    WORDPRESS_CLIENT_ID: str | None = None
    WORDPRESS_CLIENT_SECRET: str | None = None
    BLOGGER_CLIENT_ID: str | None = None
    BLOGGER_CLIENT_SECRET: str | None = None

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
    def smtp_configured(self) -> bool:
        return bool(self.SMTP_HOST)

    @property
    def email_from(self) -> str:
        return self.SMTP_FROM or self.SMTP_USER or "no-reply@postit.app"

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

    # ---- Social OAuth helpers ----
    @property
    def _api_base(self) -> str:
        return f"{self.PUBLIC_API_URL.rstrip('/')}{self.API_V1_PREFIX}"

    def oauth_redirect_uri(self, platform_id: str) -> str:
        """The OAuth redirect / callback URL to register for a platform."""
        return f"{self._api_base}/connections/{platform_id}/callback"

    def oauth_deauthorize_url(self, platform_id: str) -> str:
        """Uninstall / deauthorize callback (pinged when a user removes the app)."""
        return f"{self._api_base}/webhooks/{platform_id}/deauthorize"

    def oauth_delete_url(self, platform_id: str) -> str:
        """Data-deletion request callback (GDPR / Meta data deletion)."""
        return f"{self._api_base}/webhooks/{platform_id}/delete"

    def platform_credentials(self, platform_id: str) -> tuple[str | None, str | None]:
        key = platform_id.upper()
        return (
            getattr(self, f"{key}_CLIENT_ID", None),
            getattr(self, f"{key}_CLIENT_SECRET", None),
        )

    def oauth_configured(self, platform_id: str) -> bool:
        client_id, client_secret = self.platform_credentials(platform_id)
        return bool(client_id and client_secret)

    def platform_oauth_config(self, platform_id: str) -> dict:
        """Everything needed to wire one platform's developer console + status."""
        client_id, _ = self.platform_credentials(platform_id)
        return {
            "platform_id": platform_id,
            "configured": self.oauth_configured(platform_id),
            "client_id": client_id,
            "redirect_callback_url": self.oauth_redirect_uri(platform_id),
            "deauthorize_callback_url": self.oauth_deauthorize_url(platform_id),
            "delete_callback_url": self.oauth_delete_url(platform_id),
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
