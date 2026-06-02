"""add relative strength monitor

Revision ID: 0008_relative_strength
Revises: 0007_add_auth_workspace_usage
Create Date: 2026-05-29 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0008_relative_strength"
down_revision: str | None = "0007_add_auth_workspace_usage"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "relative_strength_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("base_symbol", sa.String(length=32), nullable=False),
        sa.Column("price", sa.Numeric(24, 10), nullable=True),
        sa.Column("btc_price", sa.Numeric(24, 10), nullable=True),
        sa.Column("return_1h", sa.Numeric(12, 6), nullable=True),
        sa.Column("return_24h", sa.Numeric(12, 6), nullable=True),
        sa.Column("return_7d", sa.Numeric(12, 6), nullable=True),
        sa.Column("return_30d", sa.Numeric(12, 6), nullable=True),
        sa.Column("btc_return_1h", sa.Numeric(12, 6), nullable=True),
        sa.Column("btc_return_24h", sa.Numeric(12, 6), nullable=True),
        sa.Column("btc_return_7d", sa.Numeric(12, 6), nullable=True),
        sa.Column("btc_return_30d", sa.Numeric(12, 6), nullable=True),
        sa.Column("excess_return_1h", sa.Numeric(12, 6), nullable=True),
        sa.Column("excess_return_24h", sa.Numeric(12, 6), nullable=True),
        sa.Column("excess_return_7d", sa.Numeric(12, 6), nullable=True),
        sa.Column("excess_return_30d", sa.Numeric(12, 6), nullable=True),
        sa.Column("relative_price", sa.Numeric(24, 10), nullable=True),
        sa.Column("relative_trend_score", sa.Numeric(12, 6), nullable=True),
        sa.Column("volume_score", sa.Numeric(12, 6), nullable=True),
        sa.Column("brsi_score", sa.Numeric(10, 4), nullable=True),
        sa.Column("brsi_change_1h", sa.Numeric(10, 4), nullable=True),
        sa.Column("brsi_change_4h", sa.Numeric(10, 4), nullable=True),
        sa.Column("brsi_change_24h", sa.Numeric(10, 4), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_relative_strength_snapshots_symbol", "relative_strength_snapshots", ["symbol"])
    op.create_index("ix_relative_strength_snapshots_base_symbol", "relative_strength_snapshots", ["base_symbol"])
    op.create_index("ix_relative_strength_snapshots_status", "relative_strength_snapshots", ["status"])
    op.create_index("ix_relative_strength_snapshots_created_at", "relative_strength_snapshots", ["created_at"])

    op.create_table(
        "relative_strength_alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("alert_type", sa.String(length=64), nullable=False),
        sa.Column("alert_level", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("brsi_score", sa.Numeric(10, 4), nullable=True),
        sa.Column("previous_brsi_score", sa.Numeric(10, 4), nullable=True),
        sa.Column("change_value", sa.Numeric(10, 4), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_relative_strength_alerts_symbol", "relative_strength_alerts", ["symbol"])
    op.create_index("ix_relative_strength_alerts_alert_type", "relative_strength_alerts", ["alert_type"])
    op.create_index("ix_relative_strength_alerts_alert_level", "relative_strength_alerts", ["alert_level"])
    op.create_index("ix_relative_strength_alerts_is_read", "relative_strength_alerts", ["is_read"])
    op.create_index("ix_relative_strength_alerts_created_at", "relative_strength_alerts", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_relative_strength_alerts_created_at", table_name="relative_strength_alerts")
    op.drop_index("ix_relative_strength_alerts_is_read", table_name="relative_strength_alerts")
    op.drop_index("ix_relative_strength_alerts_alert_level", table_name="relative_strength_alerts")
    op.drop_index("ix_relative_strength_alerts_alert_type", table_name="relative_strength_alerts")
    op.drop_index("ix_relative_strength_alerts_symbol", table_name="relative_strength_alerts")
    op.drop_table("relative_strength_alerts")

    op.drop_index("ix_relative_strength_snapshots_created_at", table_name="relative_strength_snapshots")
    op.drop_index("ix_relative_strength_snapshots_status", table_name="relative_strength_snapshots")
    op.drop_index("ix_relative_strength_snapshots_base_symbol", table_name="relative_strength_snapshots")
    op.drop_index("ix_relative_strength_snapshots_symbol", table_name="relative_strength_snapshots")
    op.drop_table("relative_strength_snapshots")
