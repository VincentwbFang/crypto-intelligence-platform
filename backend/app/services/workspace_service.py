from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import User, Workspace, WorkspaceMember, WorkspaceSubscription

WORKSPACE_ROLES = ("owner", "admin", "member", "viewer")
WORKSPACE_STATUSES = ("active", "suspended", "closed")
MEMBER_STATUSES = ("active", "invited", "removed")


class WorkspaceService:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def create_workspace(self, owner_user_id: str, name: str) -> dict[str, Any]:
        workspace_id = str(uuid4())
        workspace = Workspace(
            workspace_id=workspace_id,
            name=name.strip(),
            slug=self._unique_slug(name),
            owner_user_id=owner_user_id,
            plan=settings.DEFAULT_PLAN,
            status="active",
        )
        member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=owner_user_id,
            role="owner",
            status="active",
        )
        subscription = WorkspaceSubscription(
            workspace_id=workspace_id,
            plan=settings.DEFAULT_PLAN,
            status="active",
        )
        self.db_session.add_all([workspace, member, subscription])
        self.db_session.commit()
        self.db_session.refresh(workspace)
        return self._workspace_to_dict(workspace)

    def get_workspace(self, workspace_id: str) -> dict[str, Any] | None:
        workspace = self._workspace_row(workspace_id)
        return self._workspace_to_dict(workspace) if workspace else None

    def list_user_workspaces(self, user_id: str) -> list[dict[str, Any]]:
        statement = (
            select(Workspace, WorkspaceMember)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.workspace_id)
            .where(WorkspaceMember.user_id == user_id, WorkspaceMember.status == "active")
            .order_by(Workspace.created_at.asc())
        )
        return [
            {**self._workspace_to_dict(workspace), "role": member.role}
            for workspace, member in self.db_session.execute(statement).all()
        ]

    def update_workspace(self, workspace_id: str, data: dict[str, Any]) -> dict[str, Any]:
        workspace = self._require_workspace(workspace_id)
        if "name" in data and data["name"]:
            workspace.name = str(data["name"]).strip()
        if "plan" in data and data["plan"]:
            workspace.plan = str(data["plan"])
            subscription = self.db_session.scalar(
                select(WorkspaceSubscription).where(
                    WorkspaceSubscription.workspace_id == workspace_id
                )
            )
            if subscription:
                subscription.plan = workspace.plan
        workspace.updated_at = datetime.now(UTC)
        self.db_session.commit()
        self.db_session.refresh(workspace)
        return self._workspace_to_dict(workspace)

    def invite_member(
        self,
        workspace_id: str,
        email: str,
        role: str,
        invited_by_user_id: str,
    ) -> dict[str, Any]:
        user = self.db_session.scalar(select(User).where(User.email == email.lower()))
        if user is None:
            raise ValueError("Invited email does not belong to a registered user yet.")
        return self.add_member(workspace_id, user.user_id, role, invited_by_user_id)

    def add_member(
        self,
        workspace_id: str,
        user_id: str,
        role: str,
        invited_by_user_id: str | None = None,
    ) -> dict[str, Any]:
        self._validate_role(role)
        self._require_workspace(workspace_id)
        member = self._member_row(workspace_id, user_id)
        if member is None:
            member = WorkspaceMember(
                workspace_id=workspace_id,
                user_id=user_id,
                role=role,
                status="active",
                invited_by_user_id=invited_by_user_id,
            )
            self.db_session.add(member)
        else:
            member.role = role
            member.status = "active"
            member.updated_at = datetime.now(UTC)
        self.db_session.commit()
        self.db_session.refresh(member)
        return self._member_to_dict(member)

    def update_member_role(self, workspace_id: str, user_id: str, role: str) -> dict[str, Any]:
        self._validate_role(role)
        member = self._require_member(workspace_id, user_id)
        if member.role == "owner" and role != "owner":
            raise ValueError("Owner role cannot be demoted.")
        member.role = role
        member.updated_at = datetime.now(UTC)
        self.db_session.commit()
        self.db_session.refresh(member)
        return self._member_to_dict(member)

    def remove_member(self, workspace_id: str, user_id: str) -> dict[str, Any]:
        member = self._require_member(workspace_id, user_id)
        if member.role == "owner":
            raise ValueError("Owner cannot be removed from the workspace.")
        member.status = "removed"
        member.updated_at = datetime.now(UTC)
        self.db_session.commit()
        self.db_session.refresh(member)
        return self._member_to_dict(member)

    def list_members(self, workspace_id: str) -> list[dict[str, Any]]:
        self._require_workspace(workspace_id)
        statement = (
            select(WorkspaceMember)
            .where(WorkspaceMember.workspace_id == workspace_id)
            .order_by(WorkspaceMember.created_at.asc())
        )
        return [self._member_to_dict(member) for member in self.db_session.scalars(statement)]

    def close_workspace(self, workspace_id: str) -> dict[str, Any]:
        workspace = self._require_workspace(workspace_id)
        workspace.status = "closed"
        workspace.updated_at = datetime.now(UTC)
        self.db_session.commit()
        self.db_session.refresh(workspace)
        return self._workspace_to_dict(workspace)

    def _workspace_row(self, workspace_id: str) -> Workspace | None:
        return self.db_session.scalar(select(Workspace).where(Workspace.workspace_id == workspace_id))

    def _require_workspace(self, workspace_id: str) -> Workspace:
        workspace = self._workspace_row(workspace_id)
        if workspace is None:
            raise LookupError("Workspace not found.")
        return workspace

    def _member_row(self, workspace_id: str, user_id: str) -> WorkspaceMember | None:
        return self.db_session.scalar(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )

    def _require_member(self, workspace_id: str, user_id: str) -> WorkspaceMember:
        member = self._member_row(workspace_id, user_id)
        if member is None:
            raise LookupError("Workspace member not found.")
        return member

    def _validate_role(self, role: str) -> None:
        if role not in WORKSPACE_ROLES:
            raise ValueError(f"Invalid workspace role: {role}")

    def _unique_slug(self, name: str) -> str:
        base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "workspace"
        slug = base
        while self.db_session.scalar(select(Workspace).where(Workspace.slug == slug)):
            slug = f"{base}-{uuid4().hex[:8]}"
        return slug

    @staticmethod
    def _workspace_to_dict(workspace: Workspace) -> dict[str, Any]:
        return {
            "workspace_id": workspace.workspace_id,
            "name": workspace.name,
            "slug": workspace.slug,
            "owner_user_id": workspace.owner_user_id,
            "plan": workspace.plan,
            "status": workspace.status,
            "created_at": workspace.created_at.isoformat() if workspace.created_at else None,
            "updated_at": workspace.updated_at.isoformat() if workspace.updated_at else None,
        }

    @staticmethod
    def _member_to_dict(member: WorkspaceMember) -> dict[str, Any]:
        return {
            "id": member.id,
            "workspace_id": member.workspace_id,
            "user_id": member.user_id,
            "role": member.role,
            "status": member.status,
            "invited_by_user_id": member.invited_by_user_id,
            "created_at": member.created_at.isoformat() if member.created_at else None,
            "updated_at": member.updated_at.isoformat() if member.updated_at else None,
        }
