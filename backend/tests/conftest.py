"""Pytest fixtures - isolated SQLite DB + ASGI client."""

from __future__ import annotations

import os
import tempfile

# Configure a throwaway DB *before* importing the app/settings.
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_tmp.name}"
os.environ["REDIS_URL"] = ""
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ["PADDLE_API_KEY"] = ""
os.environ["SECRET_KEY"] = "test-secret"

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.db.base import create_all, drop_all  # noqa: E402
from app.db.seed import seed_plans, seed_platforms  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _schema():
    await create_all()
    async with SessionLocal() as db:
        await seed_platforms(db)
        await seed_plans(db)
        await db.commit()
    yield
    await drop_all()
    try:
        os.unlink(_tmp.name)
    except OSError:
        pass


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def unique_email():
    import uuid

    return f"user-{uuid.uuid4().hex[:8]}@example.com"
