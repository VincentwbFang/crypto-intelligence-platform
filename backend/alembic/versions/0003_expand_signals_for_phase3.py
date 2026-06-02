"""Expand signals table for deterministic signal payloads.

Revision ID: 0003_expand_signals_for_phase3
Revises: 0002_add_ohlcv_unique_constraint
Create Date: 2026-05-27 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_expand_signals_for_phase3"
down_revision: Union[str, None] = "0002_add_ohlcv_unique_constraint"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "signals",
        sa.Column(
            "timeframe",
            sa.String(length=16),
            server_default="1h",
            nullable=False,
        ),
    )
    op.add_column("signals", sa.Column("setup_type", sa.String(length=64), nullable=True))
    op.add_column("signals", sa.Column("risk_level", sa.String(length=32), nullable=True))
    op.add_column("signals", sa.Column("raw_payload", sa.JSON(), nullable=True))
    op.create_index("ix_signals_timeframe", "signals", ["timeframe"], unique=False)
    op.create_index("ix_signals_setup_type", "signals", ["setup_type"], unique=False)
    op.create_index("ix_signals_risk_level", "signals", ["risk_level"], unique=False)
    op.create_unique_constraint(
        "uq_signals_symbol_timeframe_timestamp_type",
        "signals",
        ["symbol", "timeframe", "timestamp", "signal_type"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_signals_symbol_timeframe_timestamp_type",
        "signals",
        type_="unique",
    )
    op.drop_index("ix_signals_risk_level", table_name="signals")
    op.drop_index("ix_signals_setup_type", table_name="signals")
    op.drop_index("ix_signals_timeframe", table_name="signals")
    op.drop_column("signals", "raw_payload")
    op.drop_column("signals", "risk_level")
    op.drop_column("signals", "setup_type")
    op.drop_column("signals", "timeframe")
