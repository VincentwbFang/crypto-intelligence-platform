from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import UserPreference


class UserPreferencesService:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def get_preferences(self, user_id: str) -> dict[str, Any]:
        preferences = self.db_session.scalar(
            select(UserPreference).where(UserPreference.user_id == user_id)
        )
        if preferences is None:
            preferences = UserPreference(
                user_id=user_id,
                default_symbol="BTC/USDT",
                default_timeframe="1h",
                theme="system",
                dashboard_layout={},
            )
            self.db_session.add(preferences)
            self.db_session.commit()
            self.db_session.refresh(preferences)
        return self._to_dict(preferences)

    def update_preferences(self, user_id: str, data: dict[str, Any]) -> dict[str, Any]:
        self.get_preferences(user_id)
        preferences = self.db_session.scalar(
            select(UserPreference).where(UserPreference.user_id == user_id)
        )
        assert preferences is not None
        for field in ("default_symbol", "default_timeframe", "theme", "dashboard_layout"):
            if field in data:
                setattr(preferences, field, data[field])
        self.db_session.commit()
        self.db_session.refresh(preferences)
        return self._to_dict(preferences)

    @staticmethod
    def _to_dict(preferences: UserPreference) -> dict[str, Any]:
        return {
            "user_id": preferences.user_id,
            "default_symbol": preferences.default_symbol,
            "default_timeframe": preferences.default_timeframe,
            "theme": preferences.theme,
            "dashboard_layout": preferences.dashboard_layout or {},
            "created_at": preferences.created_at.isoformat() if preferences.created_at else None,
            "updated_at": preferences.updated_at.isoformat() if preferences.updated_at else None,
        }
