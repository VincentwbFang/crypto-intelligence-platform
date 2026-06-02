from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.auth.permissions import can_delete_workspace, can_manage_members, can_read_workspace
from app.db.models import WorkspaceMember
from app.db.session import get_db
from app.schemas.workspaces import (
    WorkspaceCreateRequest,
    WorkspaceInviteRequest,
    WorkspaceListResponse,
    WorkspaceMemberListResponse,
    WorkspaceMemberResponse,
    WorkspaceMemberRoleUpdateRequest,
    WorkspacePlanResponse,
    WorkspaceResponse,
    WorkspaceUpdateRequest,
)
from app.services.workspace_service import WorkspaceService
from app.subscriptions.plans import get_plan_limits

router = APIRouter(tags=["workspaces"])


@router.get("", response_model=WorkspaceListResponse)
def list_workspaces(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> WorkspaceListResponse:
    return WorkspaceListResponse(
        data=WorkspaceService(db).list_user_workspaces(current_user["user_id"])
    )


@router.post("", response_model=WorkspaceResponse)
def create_workspace(
    request: WorkspaceCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> WorkspaceResponse:
    return WorkspaceResponse(
        **WorkspaceService(db).create_workspace(current_user["user_id"], request.name)
    )


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(
    workspace_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> WorkspaceResponse:
    role = _require_member(db, workspace_id, current_user["user_id"])
    workspace = WorkspaceService(db).get_workspace(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found.")
    if not can_read_workspace(role):
        raise HTTPException(status_code=403, detail="Insufficient workspace permissions.")
    return WorkspaceResponse(**workspace, role=role)


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
def update_workspace(
    workspace_id: str,
    request: WorkspaceUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> WorkspaceResponse:
    role = _require_member(db, workspace_id, current_user["user_id"])
    if role not in {"owner", "admin"}:
        raise HTTPException(status_code=403, detail="Insufficient workspace permissions.")
    try:
        return WorkspaceResponse(
            **WorkspaceService(db).update_workspace(
                workspace_id,
                request.model_dump(exclude_unset=True),
            ),
            role=role,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{workspace_id}/members", response_model=WorkspaceMemberListResponse)
def list_members(
    workspace_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> WorkspaceMemberListResponse:
    _require_member(db, workspace_id, current_user["user_id"])
    return WorkspaceMemberListResponse(data=WorkspaceService(db).list_members(workspace_id))


@router.post("/{workspace_id}/members", response_model=WorkspaceMemberResponse)
def add_member(
    workspace_id: str,
    request: WorkspaceInviteRequest,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> WorkspaceMemberResponse:
    role = _require_member(db, workspace_id, current_user["user_id"])
    if not can_manage_members(role):
        raise HTTPException(status_code=403, detail="Insufficient workspace permissions.")
    try:
        return WorkspaceMemberResponse(
            **WorkspaceService(db).invite_member(
                workspace_id,
                request.email,
                request.role,
                current_user["user_id"],
            )
        )
    except (LookupError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/{workspace_id}/members/{user_id}", response_model=WorkspaceMemberResponse)
def update_member_role(
    workspace_id: str,
    user_id: str,
    request: WorkspaceMemberRoleUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> WorkspaceMemberResponse:
    role = _require_member(db, workspace_id, current_user["user_id"])
    if not can_manage_members(role):
        raise HTTPException(status_code=403, detail="Insufficient workspace permissions.")
    try:
        return WorkspaceMemberResponse(
            **WorkspaceService(db).update_member_role(workspace_id, user_id, request.role)
        )
    except (LookupError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/{workspace_id}/members/{user_id}", response_model=WorkspaceMemberResponse)
def remove_member(
    workspace_id: str,
    user_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> WorkspaceMemberResponse:
    role = _require_member(db, workspace_id, current_user["user_id"])
    if not can_manage_members(role):
        raise HTTPException(status_code=403, detail="Insufficient workspace permissions.")
    try:
        return WorkspaceMemberResponse(**WorkspaceService(db).remove_member(workspace_id, user_id))
    except (LookupError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{workspace_id}/close", response_model=WorkspaceResponse)
def close_workspace(
    workspace_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> WorkspaceResponse:
    role = _require_member(db, workspace_id, current_user["user_id"])
    if not can_delete_workspace(role):
        raise HTTPException(status_code=403, detail="Only workspace owners can close workspaces.")
    return WorkspaceResponse(**WorkspaceService(db).close_workspace(workspace_id), role=role)


@router.get("/{workspace_id}/plan", response_model=WorkspacePlanResponse)
def get_workspace_plan(
    workspace_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> WorkspacePlanResponse:
    _require_member(db, workspace_id, current_user["user_id"])
    workspace = WorkspaceService(db).get_workspace(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found.")
    return WorkspacePlanResponse(
        workspace_id=workspace_id,
        plan=workspace["plan"],
        limits=get_plan_limits(workspace["plan"]),
    )


def _require_member(db: Session, workspace_id: str, user_id: str) -> str:
    member = db.scalar(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
            WorkspaceMember.status == "active",
        )
    )
    if member is None:
        raise HTTPException(status_code=403, detail="Workspace membership required.")
    return member.role
