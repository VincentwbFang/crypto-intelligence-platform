from app.auth.permissions import (
    can_delete_workspace,
    can_manage_billing,
    can_manage_members,
    can_read_workspace,
    can_write_workspace,
)


def test_workspace_role_permissions() -> None:
    assert can_read_workspace("viewer")
    assert not can_write_workspace("viewer")
    assert can_write_workspace("member")
    assert can_manage_members("admin")
    assert not can_manage_billing("admin")
    assert can_manage_billing("owner")
    assert can_delete_workspace("owner")
