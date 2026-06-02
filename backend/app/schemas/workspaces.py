from __future__ import annotations

from pydantic import BaseModel


class WorkspaceCreateRequest(BaseModel):
    name: str


class WorkspaceUpdateRequest(BaseModel):
    name: str | None = None


class WorkspaceResponse(BaseModel):
    workspace_id: str
    name: str
    slug: str
    owner_user_id: str
    plan: str
    status: str
    role: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class WorkspaceMemberResponse(BaseModel):
    id: int | None = None
    workspace_id: str
    user_id: str
    role: str
    status: str
    invited_by_user_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class WorkspaceInviteRequest(BaseModel):
    email: str
    role: str = "member"


class WorkspaceMemberRoleUpdateRequest(BaseModel):
    role: str


class WorkspaceListResponse(BaseModel):
    data: list[WorkspaceResponse]


class WorkspaceMemberListResponse(BaseModel):
    data: list[WorkspaceMemberResponse]


class WorkspacePlanResponse(BaseModel):
    workspace_id: str
    plan: str
    limits: dict
