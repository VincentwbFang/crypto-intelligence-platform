from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)
    full_name: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8)


class SwitchWorkspaceRequest(BaseModel):
    workspace_id: str


class AuthUserResponse(BaseModel):
    user_id: str
    email: str
    full_name: str | None = None
    is_active: bool
    is_verified: bool
    is_superuser: bool
    default_workspace_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    last_login_at: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: AuthUserResponse
    workspace: dict[str, Any] | None = None
