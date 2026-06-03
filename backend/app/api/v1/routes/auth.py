"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import client_meta, get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.schemas.common import Message
from app.schemas.token import RefreshRequest, TokenPair
from app.schemas.user import PasswordChange, UserRead
from app.services import auth as auth_service
from app.services.audit import record_audit

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, request: Request, db: AsyncSession = Depends(get_db)):
    meta = client_meta(request)
    user = await auth_service.register(
        db,
        full_name=payload.full_name,
        email=payload.email,
        password=payload.password,
        workspace_name=payload.workspace_name,
    )
    tokens = await auth_service.issue_tokens(db, user, user_agent=meta["user_agent"], ip=meta["ip"])
    await record_audit(db, action="user.registered", actor_id=user.id, **meta)
    return AuthResponse(user=UserRead.model_validate(user), tokens=tokens)


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    meta = client_meta(request)
    user = await auth_service.authenticate(db, email=payload.email, password=payload.password)
    tokens = await auth_service.issue_tokens(db, user, user_agent=meta["user_agent"], ip=meta["ip"])
    await record_audit(db, action="user.login", actor_id=user.id, **meta)
    return AuthResponse(user=UserRead.model_validate(user), tokens=tokens)


@router.post("/login/token", response_model=TokenPair, include_in_schema=True)
async def login_token(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """OAuth2 password flow — powers the Swagger 'Authorize' button (username = email)."""
    meta = client_meta(request)
    user = await auth_service.authenticate(db, email=form.username, password=form.password)
    return await auth_service.issue_tokens(db, user, user_agent=meta["user_agent"], ip=meta["ip"])


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, request: Request, db: AsyncSession = Depends(get_db)):
    meta = client_meta(request)
    return await auth_service.refresh_tokens(
        db, payload.refresh_token, user_agent=meta["user_agent"], ip=meta["ip"]
    )


@router.post("/logout", response_model=Message)
async def logout(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    await auth_service.logout(db, payload.refresh_token)
    return Message(message="Logged out.")


@router.get("/me", response_model=UserRead)
async def me(user: User = Depends(get_current_active_user)):
    return user


@router.post("/change-password", response_model=Message)
async def change_password(
    payload: PasswordChange,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    await auth_service.change_password(
        db, user, current_password=payload.current_password, new_password=payload.new_password
    )
    return Message(message="Password updated. Please sign in again.")
