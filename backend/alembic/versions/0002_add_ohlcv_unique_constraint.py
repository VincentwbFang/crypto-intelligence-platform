"""Add unique constraint for OHLCV deduplication.

Revision ID: 0002_add_ohlcv_unique_constraint
Revises: 0001_initial_schema
Create Date: 2026-05-27 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0002_add_ohlcv_unique_constraint"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_ohlcv_exchange_symbol_timeframe_timestamp",
        "ohlcv",
        ["exchange", "symbol", "timeframe", "timestamp"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_ohlcv_exchange_symbol_timeframe_timestamp",
        "ohlcv",
        type_="unique",
    )
