"""FastAPI application factory."""

from __future__ import annotations

import asyncio
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.api.v1.router import api_router
from app.api.v1.routes import health
from app.core.bootstrap import bootstrap_database
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import logger, setup_logging
from app.core.rate_limit import check_rate_limit
from app.core.redis import init_kv
from app.worker.scheduler import run_scheduler

# The Postit mark, served as the API/docs favicon (no filesystem dependency).
FAVICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Postit">'
    '<path d="M16 8 H48 a8 8 0 0 1 8 8 V40 L40 56 H16 a8 8 0 0 1 -8 -8 V16 a8 8 0 0 1 8 -8 Z" fill="#FFB627"/>'
    '<path d="M40 40 H56 L40 56 Z" fill="#E89D0C"/>'
    '<path fill-rule="evenodd" d="M24 20 H34 a8 8 0 0 1 0 16 H30 V44 H24 Z M30 26 H34 a4 4 0 0 1 0 8 H30 Z" fill="#16151A"/>'
    "</svg>"
)


def _warn_on_insecure_production_config() -> None:
    """Log loud warnings if the app boots in production with insecure defaults."""
    if not settings.is_production:
        return
    problems: list[str] = []
    if settings.DEBUG:
        problems.append("DEBUG is true")
    if settings.SECRET_KEY == "change-me":
        problems.append("SECRET_KEY is the default 'change-me'")
    if settings.OAUTH_WEBHOOK_VERIFY_TOKEN == "change-me-verify-token":
        problems.append("OAUTH_WEBHOOK_VERIFY_TOKEN is the default")
    if "*" in settings.CORS_ORIGINS:
        problems.append("CORS_ORIGINS allows '*' with credentials")
    if settings.PUBLIC_API_URL.startswith("http://localhost"):
        problems.append("PUBLIC_API_URL still points at localhost")
    if problems:
        logger.warning("INSECURE PRODUCTION CONFIG: %s", "; ".join(problems))


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await init_kv()
    _warn_on_insecure_production_config()
    # Apply migrations (+ core seed) before serving, when enabled for this deploy.
    await bootstrap_database()
    logger.info("Starting %s (%s)", settings.PROJECT_NAME, settings.ENVIRONMENT)

    stop = asyncio.Event()
    scheduler_task: asyncio.Task | None = None
    if settings.SCHEDULER_ENABLED:
        scheduler_task = asyncio.create_task(run_scheduler(stop))

    yield

    logger.info("Shutting down")
    if scheduler_task is not None:
        stop.set()
        try:
            await asyncio.wait_for(scheduler_task, timeout=5)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            scheduler_task.cancel()


def create_app() -> FastAPI:
    # Don't expose interactive docs / OpenAPI schema in production.
    expose_docs = not settings.is_production
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
        docs_url="/docs" if expose_docs else None,
        redoc_url="/redoc" if expose_docs else None,
        openapi_url="/openapi.json" if expose_docs else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    @app.middleware("http")
    async def request_context(request: Request, call_next):  # noqa: ANN001
        request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex)
        request.state.request_id = request_id
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "%s %s -> %s (%.2fms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response

    @app.middleware("http")
    async def rate_limit(request: Request, call_next):  # noqa: ANN001
        path = request.url.path
        if (
            not settings.RATE_LIMIT_ENABLED
            or path.startswith(("/healthz", "/readyz"))
            or path.endswith("/webhook")
            or "/webhooks/" in path
        ):
            return await call_next(request)
        client = request.client.host if request.client else "anon"
        allowed, remaining = await check_rate_limit(f"{client}:{path}")
        if not allowed:
            return ORJSONResponse(
                status_code=429,
                content={"error": {"code": "rate_limited", "message": "Too many requests."}},
            )
        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response

    register_exception_handlers(app)

    app.include_router(health.router)
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/", include_in_schema=False)
    async def root() -> dict:
        return {
            "service": settings.PROJECT_NAME,
            "version": "1.0.0",
            "docs": "/docs" if expose_docs else None,
            "api": settings.API_V1_PREFIX,
        }

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon() -> Response:
        return Response(content=FAVICON_SVG, media_type="image/svg+xml")

    return app


app = create_app()
