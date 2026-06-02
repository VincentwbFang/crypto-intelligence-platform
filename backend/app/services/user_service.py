from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.password import hash_password, validate_password_strength, verify_password
from app.db.models import User, UserPreference
from app.services.watchlist_service import WatchlistService
from app.services.workspace_service import WorkspaceService


class UserService:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def register_user(
        self,
        email: str,
        password: str,
        full_name: str | None = None,
    ) -> dict[str, Any]:
        normalized_email = email.strip().lower()
        if "@" not in normalized_email:
            raise ValueError("A valid email address is required.")
        if self.get_user_by_email(normalized_email) is not None:
            raise ValueError("Email is already registered.")
        password_errors = validate_password_strength(password)
        if password_errors:
            raise ValueError(" ".join(password_errors))

        user = User(
            user_id=str(uuid4()),
            email=normalized_email,
            full_name=full_name,
            password_hash=hash_password(password),
            is_active=True,
            is_verified=False,
            is_superuser=False,
        )
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        workspace = WorkspaceService(self.db_session).create_workspace(
            user.user_id,
            f"{full_name or normalized_email.split('@')[0]}'s Workspace",
        )
        user.default_workspace_id = workspace["workspace_id"]
        preferences = UserPreference(
            user_id=user.user_id,
            default_symbol="BTC/USDT",
            default_timeframe="1h",
            theme="system",
            dashboard_layout={},
        )
        self.db_session.add(preferences)
        self.db_session.commit()
        self.db_session.refresh(user)
        WatchlistService(self.db_session).create_default_watchlist(
            workspace["workspace_id"],
            user.user_id,
        )
        return self._user_to_dict(user)

    def authenticate_user(self, email: str, password: str) -> dict[str, Any] | None:
        user = self.get_user_by_email(email)
        if user is None:
            return None
        row = self.db_session.scalar(select(User).where(User.user_id == user["user_id"]))
        if row is None or not verify_password(password, row.password_hash):
            return None
        row.last_login_at = datetime.now(UTC)
        self.db_session.commit()
        self.db_session.refresh(row)
        return self._user_to_dict(row)

    def get_user(self, user_id: str) -> dict[str, Any] | None:
        user = self.db_session.scalar(select(User).where(User.user_id == user_id))
        return self._user_to_dict(user) if user else None

    def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        user = self.db_session.scalar(select(User).where(User.email == email.strip().lower()))
        return self._user_to_dict(user) if user else None

    def update_user_profile(self, user_id: str, data: dict[str, Any]) -> dict[str, Any]:
        user = self._require_user(user_id)
        if "full_name" in data:
            user.full_name = data["full_name"]
        user.updated_at = datetime.now(UTC)
        self.db_session.commit()
        self.db_session.refresh(user)
        return self._user_to_dict(user)

    def deactivate_user(self, user_id: str) -> dict[str, Any]:
        user = self._require_user(user_id)
        user.is_active = False
        user.updated_at = datetime.now(UTC)
        self.db_session.commit()
        self.db_session.refresh(user)
        return self._user_to_dict(user)

    def _require_user(self, user_id: str) -> User:
        user = self.db_session.scalar(select(User).where(User.user_id == user_id))
        if user is None:
            raise LookupError("User not found.")
        return user

    @staticmethod
    def _user_to_dict(user: User) -> dict[str, Any]:
        return {
            "user_id": user.user_id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "is_superuser": user.is_superuser,
            "default_workspace_id": user.default_workspace_id,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        }
