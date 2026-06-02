"""Add Phase 8 auth, workspace, watchlist, and usage tables.

Revision ID: 0007_add_auth_workspace_usage
Revises: 0006_add_paper_trading_tables
Create Date: 2026-05-28 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007_add_auth_workspace_usage"
down_revision: str | None = "0006_add_paper_trading_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("default_workspace_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_users_user_id"), "users", ["user_id"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)
    op.create_index(op.f("ix_users_default_workspace_id"), "users", ["default_workspace_id"], unique=False)

    op.create_table(
        "workspaces",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workspace_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False),
        sa.Column("plan", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
        sa.UniqueConstraint("workspace_id"),
    )
    op.create_index(op.f("ix_workspaces_workspace_id"), "workspaces", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_workspaces_slug"), "workspaces", ["slug"], unique=False)
    op.create_index(op.f("ix_workspaces_owner_user_id"), "workspaces", ["owner_user_id"], unique=False)
    op.create_index(op.f("ix_workspaces_plan"), "workspaces", ["plan"], unique=False)
    op.create_index(op.f("ix_workspaces_status"), "workspaces", ["status"], unique=False)

    op.create_table(
        "workspace_members",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workspace_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("invited_by_user_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "user_id", name="uq_workspace_member"),
    )
    op.create_index(op.f("ix_workspace_members_workspace_id"), "workspace_members", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_workspace_members_user_id"), "workspace_members", ["user_id"], unique=False)
    op.create_index(op.f("ix_workspace_members_role"), "workspace_members", ["role"], unique=False)
    op.create_index(op.f("ix_workspace_members_status"), "workspace_members", ["status"], unique=False)
    op.create_index(op.f("ix_workspace_members_invited_by_user_id"), "workspace_members", ["invited_by_user_id"], unique=False)

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_id"),
    )
    op.create_index(op.f("ix_refresh_tokens_token_id"), "refresh_tokens", ["token_id"], unique=False)
    op.create_index(op.f("ix_refresh_tokens_user_id"), "refresh_tokens", ["user_id"], unique=False)
    op.create_index(op.f("ix_refresh_tokens_token_hash"), "refresh_tokens", ["token_hash"], unique=False)
    op.create_index(op.f("ix_refresh_tokens_expires_at"), "refresh_tokens", ["expires_at"], unique=False)
    op.create_index(op.f("ix_refresh_tokens_revoked_at"), "refresh_tokens", ["revoked_at"], unique=False)

    op.create_table(
        "user_preferences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("default_symbol", sa.String(length=32), nullable=False),
        sa.Column("default_timeframe", sa.String(length=16), nullable=False),
        sa.Column("theme", sa.String(length=32), nullable=False),
        sa.Column("dashboard_layout", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_user_preferences_user_id"), "user_preferences", ["user_id"], unique=False)

    op.create_table(
        "watchlists",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("watchlist_id", sa.String(length=64), nullable=False),
        sa.Column("workspace_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("watchlist_id"),
    )
    op.create_index(op.f("ix_watchlists_watchlist_id"), "watchlists", ["watchlist_id"], unique=False)
    op.create_index(op.f("ix_watchlists_workspace_id"), "watchlists", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_watchlists_created_by_user_id"), "watchlists", ["created_by_user_id"], unique=False)

    op.create_table(
        "watchlist_symbols",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("watchlist_id", sa.String(length=64), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("watchlist_id", "symbol", name="uq_watchlist_symbol"),
    )
    op.create_index(op.f("ix_watchlist_symbols_watchlist_id"), "watchlist_symbols", ["watchlist_id"], unique=False)
    op.create_index(op.f("ix_watchlist_symbols_symbol"), "watchlist_symbols", ["symbol"], unique=False)

    op.create_table(
        "usage_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workspace_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_usage_events_workspace_id"), "usage_events", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_usage_events_user_id"), "usage_events", ["user_id"], unique=False)
    op.create_index(op.f("ix_usage_events_event_type"), "usage_events", ["event_type"], unique=False)
    op.create_index(op.f("ix_usage_events_created_at"), "usage_events", ["created_at"], unique=False)

    op.create_table(
        "workspace_subscriptions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workspace_id", sa.String(length=64), nullable=False),
        sa.Column("plan", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("external_customer_id", sa.String(length=255), nullable=True),
        sa.Column("external_subscription_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id"),
    )
    op.create_index(op.f("ix_workspace_subscriptions_workspace_id"), "workspace_subscriptions", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_workspace_subscriptions_plan"), "workspace_subscriptions", ["plan"], unique=False)
    op.create_index(op.f("ix_workspace_subscriptions_status"), "workspace_subscriptions", ["status"], unique=False)

    for table_name in ("alerts", "backtest_runs", "paper_accounts", "paper_orders", "paper_trades"):
        op.add_column(table_name, sa.Column("workspace_id", sa.String(length=64), nullable=True))
        op.add_column(table_name, sa.Column("created_by_user_id", sa.String(length=64), nullable=True))
        op.create_index(op.f(f"ix_{table_name}_workspace_id"), table_name, ["workspace_id"], unique=False)
        op.create_index(op.f(f"ix_{table_name}_created_by_user_id"), table_name, ["created_by_user_id"], unique=False)

    for table_name in ("backtest_trades", "paper_positions", "paper_equity_snapshots"):
        op.add_column(table_name, sa.Column("workspace_id", sa.String(length=64), nullable=True))
        op.create_index(op.f(f"ix_{table_name}_workspace_id"), table_name, ["workspace_id"], unique=False)


def downgrade() -> None:
    for table_name in ("backtest_trades", "paper_positions", "paper_equity_snapshots"):
        op.drop_index(op.f(f"ix_{table_name}_workspace_id"), table_name=table_name)
        op.drop_column(table_name, "workspace_id")

    for table_name in ("alerts", "backtest_runs", "paper_accounts", "paper_orders", "paper_trades"):
        op.drop_index(op.f(f"ix_{table_name}_created_by_user_id"), table_name=table_name)
        op.drop_index(op.f(f"ix_{table_name}_workspace_id"), table_name=table_name)
        op.drop_column(table_name, "created_by_user_id")
        op.drop_column(table_name, "workspace_id")

    op.drop_index(op.f("ix_workspace_subscriptions_status"), table_name="workspace_subscriptions")
    op.drop_index(op.f("ix_workspace_subscriptions_plan"), table_name="workspace_subscriptions")
    op.drop_index(op.f("ix_workspace_subscriptions_workspace_id"), table_name="workspace_subscriptions")
    op.drop_table("workspace_subscriptions")
    op.drop_index(op.f("ix_usage_events_created_at"), table_name="usage_events")
    op.drop_index(op.f("ix_usage_events_event_type"), table_name="usage_events")
    op.drop_index(op.f("ix_usage_events_user_id"), table_name="usage_events")
    op.drop_index(op.f("ix_usage_events_workspace_id"), table_name="usage_events")
    op.drop_table("usage_events")
    op.drop_index(op.f("ix_watchlist_symbols_symbol"), table_name="watchlist_symbols")
    op.drop_index(op.f("ix_watchlist_symbols_watchlist_id"), table_name="watchlist_symbols")
    op.drop_table("watchlist_symbols")
    op.drop_index(op.f("ix_watchlists_created_by_user_id"), table_name="watchlists")
    op.drop_index(op.f("ix_watchlists_workspace_id"), table_name="watchlists")
    op.drop_index(op.f("ix_watchlists_watchlist_id"), table_name="watchlists")
    op.drop_table("watchlists")
    op.drop_index(op.f("ix_user_preferences_user_id"), table_name="user_preferences")
    op.drop_table("user_preferences")
    op.drop_index(op.f("ix_refresh_tokens_revoked_at"), table_name="refresh_tokens")
    op.drop_index(op.f("ix_refresh_tokens_expires_at"), table_name="refresh_tokens")
    op.drop_index(op.f("ix_refresh_tokens_token_hash"), table_name="refresh_tokens")
    op.drop_index(op.f("ix_refresh_tokens_user_id"), table_name="refresh_tokens")
    op.drop_index(op.f("ix_refresh_tokens_token_id"), table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
    op.drop_index(op.f("ix_workspace_members_invited_by_user_id"), table_name="workspace_members")
    op.drop_index(op.f("ix_workspace_members_status"), table_name="workspace_members")
    op.drop_index(op.f("ix_workspace_members_role"), table_name="workspace_members")
    op.drop_index(op.f("ix_workspace_members_user_id"), table_name="workspace_members")
    op.drop_index(op.f("ix_workspace_members_workspace_id"), table_name="workspace_members")
    op.drop_table("workspace_members")
    op.drop_index(op.f("ix_workspaces_status"), table_name="workspaces")
    op.drop_index(op.f("ix_workspaces_plan"), table_name="workspaces")
    op.drop_index(op.f("ix_workspaces_owner_user_id"), table_name="workspaces")
    op.drop_index(op.f("ix_workspaces_slug"), table_name="workspaces")
    op.drop_index(op.f("ix_workspaces_workspace_id"), table_name="workspaces")
    op.drop_table("workspaces")
    op.drop_index(op.f("ix_users_default_workspace_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_user_id"), table_name="users")
    op.drop_table("users")
