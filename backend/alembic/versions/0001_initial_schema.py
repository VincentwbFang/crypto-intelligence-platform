"""Create initial market intelligence tables.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-26 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("coingecko_id", sa.String(length=255), nullable=True),
        sa.Column("chain", sa.String(length=64), nullable=True),
        sa.Column("category", sa.String(length=64), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("coingecko_id"),
    )
    op.create_index("ix_tokens_symbol", "tokens", ["symbol"], unique=False)
    op.create_index("ix_tokens_chain", "tokens", ["chain"], unique=False)
    op.create_index("ix_tokens_category", "tokens", ["category"], unique=False)

    op.create_table(
        "ohlcv",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("exchange", sa.String(length=64), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("timeframe", sa.String(length=16), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("open", sa.Numeric(precision=24, scale=10), nullable=False),
        sa.Column("high", sa.Numeric(precision=24, scale=10), nullable=False),
        sa.Column("low", sa.Numeric(precision=24, scale=10), nullable=False),
        sa.Column("close", sa.Numeric(precision=24, scale=10), nullable=False),
        sa.Column("volume", sa.Numeric(precision=32, scale=10), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ohlcv_exchange", "ohlcv", ["exchange"], unique=False)
    op.create_index("ix_ohlcv_symbol", "ohlcv", ["symbol"], unique=False)
    op.create_index("ix_ohlcv_timeframe", "ohlcv", ["timeframe"], unique=False)
    op.create_index("ix_ohlcv_timestamp", "ohlcv", ["timestamp"], unique=False)

    op.create_table(
        "signals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("signal_type", sa.String(length=64), nullable=False),
        sa.Column("score", sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column("direction", sa.String(length=16), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_signals_symbol", "signals", ["symbol"], unique=False)
    op.create_index("ix_signals_timestamp", "signals", ["timestamp"], unique=False)
    op.create_index("ix_signals_signal_type", "signals", ["signal_type"], unique=False)

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("alert_type", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_alerts_symbol", "alerts", ["symbol"], unique=False)
    op.create_index("ix_alerts_timestamp", "alerts", ["timestamp"], unique=False)
    op.create_index("ix_alerts_alert_type", "alerts", ["alert_type"], unique=False)
    op.create_index("ix_alerts_severity", "alerts", ["severity"], unique=False)
    op.create_index("ix_alerts_status", "alerts", ["status"], unique=False)

    op.create_table(
        "paper_trades",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("side", sa.String(length=16), nullable=False),
        sa.Column("entry_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("entry_price", sa.Numeric(precision=24, scale=10), nullable=False),
        sa.Column("exit_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("exit_price", sa.Numeric(precision=24, scale=10), nullable=True),
        sa.Column("size", sa.Numeric(precision=32, scale=10), nullable=False),
        sa.Column("pnl", sa.Numeric(precision=32, scale=10), nullable=True),
        sa.Column("strategy_name", sa.String(length=128), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_paper_trades_symbol", "paper_trades", ["symbol"], unique=False)
    op.create_index("ix_paper_trades_side", "paper_trades", ["side"], unique=False)
    op.create_index("ix_paper_trades_entry_time", "paper_trades", ["entry_time"], unique=False)
    op.create_index(
        "ix_paper_trades_strategy_name",
        "paper_trades",
        ["strategy_name"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_paper_trades_strategy_name", table_name="paper_trades")
    op.drop_index("ix_paper_trades_entry_time", table_name="paper_trades")
    op.drop_index("ix_paper_trades_side", table_name="paper_trades")
    op.drop_index("ix_paper_trades_symbol", table_name="paper_trades")
    op.drop_table("paper_trades")

    op.drop_index("ix_alerts_status", table_name="alerts")
    op.drop_index("ix_alerts_severity", table_name="alerts")
    op.drop_index("ix_alerts_alert_type", table_name="alerts")
    op.drop_index("ix_alerts_timestamp", table_name="alerts")
    op.drop_index("ix_alerts_symbol", table_name="alerts")
    op.drop_table("alerts")

    op.drop_index("ix_signals_signal_type", table_name="signals")
    op.drop_index("ix_signals_timestamp", table_name="signals")
    op.drop_index("ix_signals_symbol", table_name="signals")
    op.drop_table("signals")

    op.drop_index("ix_ohlcv_timestamp", table_name="ohlcv")
    op.drop_index("ix_ohlcv_timeframe", table_name="ohlcv")
    op.drop_index("ix_ohlcv_symbol", table_name="ohlcv")
    op.drop_index("ix_ohlcv_exchange", table_name="ohlcv")
    op.drop_table("ohlcv")

    op.drop_index("ix_tokens_category", table_name="tokens")
    op.drop_index("ix_tokens_chain", table_name="tokens")
    op.drop_index("ix_tokens_symbol", table_name="tokens")
    op.drop_table("tokens")

