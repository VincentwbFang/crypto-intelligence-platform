from __future__ import annotations

ROLE_ORDER = ("viewer", "member", "admin", "owner")


def can_read_workspace(role: str | None) -> bool:
    return role in ROLE_ORDER


def can_write_workspace(role: str | None) -> bool:
    return role in {"owner", "admin", "member"}


def can_manage_members(role: str | None) -> bool:
    return role in {"owner", "admin"}


def can_manage_billing(role: str | None) -> bool:
    return role == "owner"


def can_delete_workspace(role: str | None) -> bool:
    return role == "owner"


def has_any_role(role: str | None, required_roles: list[str]) -> bool:
    return role in set(required_roles)
