"""FastAPI application factory."""

from __future__ import annotations

import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.api.v1.router import api_router
from app.api.v1.routes import health
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import logger, setup_logging
from app.core.rate_limit import check_rate_limit
from app.core.redis import init_kv


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await init_kv()
    logger.info("Starting %s (%s)", settings.PROJECT_NAME, settings.ENVIRONMENT)
    yield
    logger.info("Shutting down")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
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
        if not settings.RATE_LIMIT_ENABLED or path.startswith(("/healthz", "/readyz")) or path.endswith("/webhook"):
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
            "docs": "/docs",
            "api": settings.API_V1_PREFIX,
        }

    return app


app = create_app()
