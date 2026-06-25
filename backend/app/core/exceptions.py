"""Application error hierarchy + consistent error-envelope handlers."""

from __future__ import annotations

import traceback
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from sqlalchemy.exc import IntegrityError, InterfaceError, OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import logger


class AppError(Exception):
    """Base class for expected, mapped application errors."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    code: str = "error"
    message: str = "Something went wrong."

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        status_code: int | None = None,
        details: Any = None,
    ) -> None:
        self.message = message or self.message
        self.code = code or self.code
        self.status_code = status_code or self.status_code
        self.details = details
        super().__init__(self.message)


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"
    message = "Resource not found."


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT
    code = "conflict"
    message = "Resource already exists."


class AuthError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "unauthorized"
    message = "Not authenticated."


class PermissionError_(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "forbidden"
    message = "You don't have permission to do that."


class ValidationError_(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    code = "validation_error"
    message = "Invalid input."


class RateLimitError(AppError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    code = "rate_limited"
    message = "Too many requests. Please slow down."


class BillingError(AppError):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    code = "billing_error"
    message = "Billing operation failed."


class ServiceUnavailableError(AppError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = "service_unavailable"
    message = "This feature is not configured."


def _envelope(code: str, message: str, details: Any = None, request: Request | None = None) -> dict:
    body: dict[str, Any] = {"error": {"code": code, "message": message}}
    if details is not None:
        body["error"]["details"] = details
    if request is not None:
        rid = getattr(request.state, "request_id", None)
        if rid:
            body["error"]["request_id"] = rid
    return body


async def _persist_error(
    request: Request, exc: Exception, *, status_code: int, code: str, message: str
) -> None:
    """Write a server error (5xx) to the DB. Best-effort: never raises."""
    # If the DB itself is the failure (e.g. host unreachable / connection refused),
    # persisting to that same DB cannot succeed and would emit a second full
    # traceback per request, drowning the real error. Skip it with one concise line.
    if isinstance(exc, (OperationalError, InterfaceError)):
        logger.warning("DB unavailable; not persisting error log (%s)", exc.__class__.__name__)
        return

    # Imported lazily to avoid a circular import at module load.
    from app.core.database import SessionLocal
    from app.models.error_log import ErrorLog

    try:
        stack = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))[:20000]
        async with SessionLocal() as session:
            session.add(
                ErrorLog(
                    request_id=getattr(request.state, "request_id", None),
                    method=request.method,
                    path=request.url.path[:255],
                    status_code=status_code,
                    error_code=code,
                    message=(message or str(exc) or "Unhandled error")[:2000],
                    stack=stack,
                    user_id=getattr(request.state, "user_id", None),
                    ip=(request.client.host if request.client else None),
                    user_agent=(request.headers.get("user-agent") or "")[:255] or None,
                )
            )
            await session.commit()
    except Exception as persist_exc:  # pragma: no cover - must never mask the original error
        # One concise line, not a full traceback, so it can't bury the real error.
        logger.warning("Failed to persist error log: %s", persist_exc)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(request: Request, exc: AppError) -> ORJSONResponse:
        if exc.status_code >= 500:
            await _persist_error(
                request, exc, status_code=exc.status_code, code=exc.code, message=exc.message
            )
        return ORJSONResponse(
            status_code=exc.status_code,
            content=_envelope(exc.code, exc.message, exc.details, request),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation(request: Request, exc: RequestValidationError) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_envelope("validation_error", "Invalid input.", exc.errors(), request),
        )

    @app.exception_handler(IntegrityError)
    async def _integrity(request: Request, exc: IntegrityError) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=_envelope("conflict", "That operation conflicts with existing data.", None, request),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http(request: Request, exc: StarletteHTTPException) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=exc.status_code,
            content=_envelope("http_error", str(exc.detail), None, request),
        )

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> ORJSONResponse:
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        await _persist_error(
            request,
            exc,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="internal_error",
            message=str(exc) or "An unexpected error occurred.",
        )
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_envelope("internal_error", "An unexpected error occurred.", None, request),
        )
