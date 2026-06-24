"""Async SQLAlchemy engine + session management."""

from __future__ import annotations

import ssl
from collections.abc import AsyncGenerator
from urllib.parse import urlsplit

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

_LOCAL_HOSTS = {"", "localhost", "127.0.0.1", "::1"}


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def _mysql_ssl_context() -> ssl.SSLContext:
    """TLS context for MySQL. Verifies against DB_SSL_CA when provided, otherwise
    encrypts without CA verification — matching MySQL's ``ssl-mode=REQUIRED``."""
    if settings.DB_SSL_CA:
        return ssl.create_default_context(cafile=settings.DB_SSL_CA)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def ssl_connect_args() -> dict:
    """connect_args enabling TLS for remote MySQL (empty for sqlite/local).

    Shared by the app engine and Alembic so migrations use the same TLS. Auto-on
    for non-local hosts (e.g. Aiven) unless DB_SSL is set explicitly.
    """
    if settings.is_sqlite:
        return {}
    use_ssl = settings.DB_SSL
    if use_ssl is None:
        host = (urlsplit(settings.DATABASE_URL).hostname or "").lower()
        use_ssl = host not in _LOCAL_HOSTS
    return {"ssl": _mysql_ssl_context()} if use_ssl else {}


def _engine_kwargs() -> dict:
    if settings.is_sqlite:
        # SQLite (aiosqlite) doesn't use a server-side connection pool.
        return {"connect_args": {"check_same_thread": False}}
    kwargs: dict = {
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_recycle": settings.DB_POOL_RECYCLE,
        "pool_pre_ping": True,
    }
    ssl_args = ssl_connect_args()
    if ssl_args:
        kwargs["connect_args"] = ssl_args
    return kwargs


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.SQL_ECHO,
    future=True,
    **_engine_kwargs(),
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a transactional session.

    Commits on success, rolls back on exception, always closes.
    """
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
