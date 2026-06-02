from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class UserProfileUpdateRequest(BaseModel):
    full_name: str | None = None


class UserPreferenceResponse(BaseModel):
    user_id: str
    default_symbol: str
    default_timeframe: str
    theme: str
    dashboard_layout: dict[str, Any]
    created_at: str | None = None
    updated_at: str | None = None


class UserPreferenceUpdateRequest(BaseModel):
    default_symbol: str | None = None
    default_timeframe: str | None = None
    theme: str | None = None
    dashboard_layout: dict[str, Any] | None = None
