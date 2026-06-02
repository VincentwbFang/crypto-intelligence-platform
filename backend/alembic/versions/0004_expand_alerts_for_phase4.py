"""Expand alerts table for Phase 4 alert engine.

Revision ID: 0004_expand_alerts_for_phase4
Revises: 0003_expand_signals_for_phase3
Create Date: 2026-05-27 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004_expand_alerts_for_phase4"
down_revision: Union[str, None] = "0003_expand_signals_for_phase3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "alerts",
        sa.Column(
            "timeframe",
            sa.String(length=16),
            server_default="1h",
            nullable=False,
        ),
    )
    op.add_column(
        "alerts",
        sa.Column(
            "title",
            sa.String(length=255),
            server_default="Market alert",
            nullable=False,
        ),
    )
    op.add_column("alerts", sa.Column("source", sa.String(length=64), nullable=True))
    op.add_column("alerts", sa.Column("signal_score", sa.Numeric(10, 4), nullable=True))
    op.add_column("alerts", sa.Column("risk_level", sa.String(length=32), nullable=True))
    op.add_column("alerts", sa.Column("setup_type", sa.String(length=64), nullable=True))
    op.add_column(
        "alerts",
        sa.Column(
            "dedup_key",
            sa.String(length=512),
            server_default="legacy-alert",
            nullable=False,
        ),
    )
    op.add_column("alerts", sa.Column("raw_payload", sa.JSON(), nullable=True))
    op.add_column(
        "alerts",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.add_column("alerts", sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True))

    op.create_index("ix_alerts_timeframe", "alerts", ["timeframe"], unique=False)
    op.create_index("ix_alerts_source", "alerts", ["source"], unique=False)
    op.create_index("ix_alerts_risk_level", "alerts", ["risk_level"], unique=False)
    op.create_index("ix_alerts_setup_type", "alerts", ["setup_type"], unique=False)
    op.create_index("ix_alerts_dedup_key", "alerts", ["dedup_key"], unique=False)
    op.create_index("ix_alerts_created_at", "alerts", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_alerts_created_at", table_name="alerts")
    op.drop_index("ix_alerts_dedup_key", table_name="alerts")
    op.drop_index("ix_alerts_setup_type", table_name="alerts")
    op.drop_index("ix_alerts_risk_level", table_name="alerts")
    op.drop_index("ix_alerts_source", table_name="alerts")
    op.drop_index("ix_alerts_timeframe", table_name="alerts")

    op.drop_column("alerts", "resolved_at")
    op.drop_column("alerts", "updated_at")
    op.drop_column("alerts", "raw_payload")
    op.drop_column("alerts", "dedup_key")
    op.drop_column("alerts", "setup_type")
    op.drop_column("alerts", "risk_level")
    op.drop_column("alerts", "signal_score")
    op.drop_column("alerts", "source")
    op.drop_column("alerts", "title")
    op.drop_column("alerts", "timeframe")
