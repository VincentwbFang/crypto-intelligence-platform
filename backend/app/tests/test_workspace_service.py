from sqlalchemy.orm import Session

from app.services.user_service import UserService
from app.services.workspace_service import WorkspaceService


def test_workspace_service_create_member_role_and_close(db_session: Session) -> None:
    user_service = UserService(db_session)
    owner = user_service.register_user("owner@example.com", "Password123", "Owner")
    member = user_service.register_user("member@example.com", "Password123", "Member")

    workspace_service = WorkspaceService(db_session)
    workspace = workspace_service.create_workspace(owner["user_id"], "Research Desk")
    workspaces = workspace_service.list_user_workspaces(owner["user_id"])
    assert any(item["workspace_id"] == workspace["workspace_id"] for item in workspaces)

    added = workspace_service.add_member(workspace["workspace_id"], member["user_id"], "viewer")
    assert added["role"] == "viewer"
    updated = workspace_service.update_member_role(workspace["workspace_id"], member["user_id"], "member")
    assert updated["role"] == "member"
    removed = workspace_service.remove_member(workspace["workspace_id"], member["user_id"])
    assert removed["status"] == "removed"
    closed = workspace_service.close_workspace(workspace["workspace_id"])
    assert closed["status"] == "closed"
