from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.permissions import has_any_role
from app.auth.tokens import verify_access_token
from app.core.config import settings
from app.db.models import User, Workspace, WorkspaceMember
from app.db.session import get_db


def optional_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict[str, Any] | None:
    if not authorization:
        return None
    try:
        return _load_user_from_authorization(authorization, db)
    except HTTPException:
        return None


def require_auth_if_enabled(
    current_user: dict[str, Any] | None = Depends(optional_current_user),
) -> dict[str, Any] | None:
    if settings.ENABLE_AUTH and current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )
    return current_user


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )
    return _load_user_from_authorization(authorization, db)


def get_current_active_user(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    if not current_user["is_active"]:
        raise HTTPException(status_code=403, detail="User is inactive.")
    return current_user


def get_current_workspace(
    current_user: dict[str, Any] = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    workspace_id = current_user.get("workspace_id") or current_user.get("default_workspace_id")
    if not workspace_id:
        raise HTTPException(status_code=403, detail="No workspace is selected.")
    workspace = db.scalar(select(Workspace).where(Workspace.workspace_id == workspace_id))
    if workspace is None or workspace.status != "active":
        raise HTTPException(status_code=403, detail="Workspace is not available.")
    member = db.scalar(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user["user_id"],
            WorkspaceMember.status == "active",
        )
    )
    if member is None:
        raise HTTPException(status_code=403, detail="Workspace membership required.")
    return {
        "workspace_id": workspace.workspace_id,
        "name": workspace.name,
        "slug": workspace.slug,
        "owner_user_id": workspace.owner_user_id,
        "plan": workspace.plan,
        "status": workspace.status,
        "role": member.role,
    }


def optional_current_workspace(
    current_user: dict[str, Any] | None = Depends(optional_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any] | None:
    if current_user is None:
        return None
    try:
        return _workspace_for_user(current_user, db)
    except HTTPException:
        return None


def require_workspace_member(
    workspace: dict[str, Any] = Depends(get_current_workspace),
) -> dict[str, Any]:
    return workspace


def require_workspace_role(required_roles: list[str]) -> Callable[..., dict[str, Any]]:
    def dependency(workspace: dict[str, Any] = Depends(get_current_workspace)) -> dict[str, Any]:
        if not has_any_role(workspace.get("role"), required_roles):
            raise HTTPException(status_code=403, detail="Insufficient workspace permissions.")
        return workspace

    return dependency


def _load_user_from_authorization(authorization: str, db: Session) -> dict[str, Any]:
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid authorization header.")
    try:
        payload = verify_access_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    user = db.scalar(select(User).where(User.user_id == payload["sub"]))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found.")
    return {
        "id": user.id,
        "user_id": user.user_id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "is_superuser": user.is_superuser,
        "default_workspace_id": user.default_workspace_id,
        "workspace_id": payload.get("workspace_id"),
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
    }


def _workspace_for_user(current_user: dict[str, Any], db: Session) -> dict[str, Any]:
    workspace_id = current_user.get("workspace_id") or current_user.get("default_workspace_id")
    if not workspace_id:
        raise HTTPException(status_code=403, detail="No workspace is selected.")
    workspace = db.scalar(select(Workspace).where(Workspace.workspace_id == workspace_id))
    member = db.scalar(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user["user_id"],
            WorkspaceMember.status == "active",
        )
    )
    if workspace is None or member is None or workspace.status != "active":
        raise HTTPException(status_code=403, detail="Workspace membership required.")
    return {
        "workspace_id": workspace.workspace_id,
        "name": workspace.name,
        "slug": workspace.slug,
        "owner_user_id": workspace.owner_user_id,
        "plan": workspace.plan,
        "status": workspace.status,
        "role": member.role,
    }
