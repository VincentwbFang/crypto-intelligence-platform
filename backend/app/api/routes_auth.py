from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user, get_current_workspace
from app.auth.password import hash_password, validate_password_strength, verify_password
from app.auth.tokens import (
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    verify_refresh_token,
)
from app.core.config import settings
from app.db.models import RefreshToken, User, WorkspaceMember
from app.db.session import get_db
from app.schemas.auth import (
    AuthUserResponse,
    LoginRequest,
    LogoutRequest,
    PasswordChangeRequest,
    RefreshTokenRequest,
    RegisterRequest,
    SwitchWorkspaceRequest,
    TokenResponse,
)
from app.services.user_service import UserService
from app.services.workspace_service import WorkspaceService

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        user = UserService(db).register_user(
            request.email,
            request.password,
            request.full_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    workspace = _default_workspace(db, user["user_id"], user["default_workspace_id"])
    return _issue_token_response(db, user, workspace)


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = UserService(db).authenticate_user(request.email, request.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    workspace = _default_workspace(db, user["user_id"], user["default_workspace_id"])
    return _issue_token_response(db, user, workspace)


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: RefreshTokenRequest, db: Session = Depends(get_db)) -> TokenResponse:
    token_hash = hash_refresh_token(request.refresh_token)
    row = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    if row is None or row.revoked_at is not None or _as_aware(row.expires_at) <= datetime.now(UTC):
        raise HTTPException(status_code=401, detail="Invalid refresh token.")
    if not verify_refresh_token(request.refresh_token, row.token_hash):
        raise HTTPException(status_code=401, detail="Invalid refresh token.")
    user = UserService(db).get_user(row.user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found.")
    workspace = _default_workspace(db, user["user_id"], user["default_workspace_id"])
    return _issue_token_response(db, user, workspace)


@router.post("/logout")
def logout(request: LogoutRequest, db: Session = Depends(get_db)) -> dict[str, bool]:
    token_hash = hash_refresh_token(request.refresh_token)
    row = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    if row is not None:
        row.revoked_at = datetime.now(UTC)
        db.commit()
    return {"logged_out": True}


@router.get("/me")
def me(
    current_user: dict = Depends(get_current_active_user),
    workspace: dict = Depends(get_current_workspace),
) -> dict:
    return {"user": current_user, "workspace": workspace}


@router.post("/switch-workspace", response_model=TokenResponse)
def switch_workspace(
    request: SwitchWorkspaceRequest,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> TokenResponse:
    member = db.scalar(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == request.workspace_id,
            WorkspaceMember.user_id == current_user["user_id"],
            WorkspaceMember.status == "active",
        )
    )
    if member is None:
        raise HTTPException(status_code=403, detail="Workspace membership required.")
    workspace = WorkspaceService(db).get_workspace(request.workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found.")
    workspace["role"] = member.role
    return _issue_token_response(db, current_user, workspace)


@router.post("/change-password")
def change_password(
    request: PasswordChangeRequest,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict[str, bool]:
    user = db.scalar(select(User).where(User.user_id == current_user["user_id"]))
    if user is None or not verify_password(request.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")
    errors = validate_password_strength(request.new_password)
    if errors:
        raise HTTPException(status_code=400, detail=" ".join(errors))
    user.password_hash = hash_password(request.new_password)
    user.updated_at = datetime.now(UTC)
    db.commit()
    return {"password_changed": True}


def _issue_token_response(db: Session, user: dict, workspace: dict | None) -> TokenResponse:
    workspace_id = workspace["workspace_id"] if workspace else None
    access_token = create_access_token(user["user_id"], workspace_id)
    refresh_token, refresh_hash = create_refresh_token()
    db.add(
        RefreshToken(
            token_id=hash_refresh_token(refresh_token)[:32],
            user_id=user["user_id"],
            token_hash=refresh_hash,
            expires_at=datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
    )
    db.commit()
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=AuthUserResponse(**user),
        workspace=workspace,
    )


def _default_workspace(db: Session, user_id: str, default_workspace_id: str | None) -> dict | None:
    workspaces = WorkspaceService(db).list_user_workspaces(user_id)
    if default_workspace_id:
        for workspace in workspaces:
            if workspace["workspace_id"] == default_workspace_id:
                return workspace
    return workspaces[0] if workspaces else None


def _as_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value
