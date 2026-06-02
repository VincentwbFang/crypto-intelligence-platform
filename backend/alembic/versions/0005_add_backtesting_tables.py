"""Add Phase 6 backtesting tables.

Revision ID: 0005_add_backtesting_tables
Revises: 0004_expand_alerts_for_phase4
Create Date: 2026-05-27 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0005_add_backtesting_tables"
down_revision: Union[str, None] = "0004_expand_alerts_for_phase4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "backtest_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("timeframe", sa.String(length=16), nullable=False),
        sa.Column("strategy_name", sa.String(length=128), nullable=False),
        sa.Column("parameters", sa.JSON(), nullable=True),
        sa.Column("initial_capital", sa.Numeric(24, 8), nullable=False),
        sa.Column("final_equity", sa.Numeric(24, 8), nullable=True),
        sa.Column("total_return_pct", sa.Numeric(12, 6), nullable=True),
        sa.Column("max_drawdown_pct", sa.Numeric(12, 6), nullable=True),
        sa.Column("sharpe_ratio", sa.Numeric(12, 6), nullable=True),
        sa.Column("win_rate", sa.Numeric(12, 6), nullable=True),
        sa.Column("profit_factor", sa.Numeric(18, 6), nullable=True),
        sa.Column("total_trades", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("metrics", sa.JSON(), nullable=True),
        sa.Column("equity_curve", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id"),
    )
    op.create_index("ix_backtest_runs_run_id", "backtest_runs", ["run_id"], unique=False)
    op.create_index("ix_backtest_runs_symbol", "backtest_runs", ["symbol"], unique=False)
    op.create_index("ix_backtest_runs_timeframe", "backtest_runs", ["timeframe"], unique=False)
    op.create_index(
        "ix_backtest_runs_strategy_name",
        "backtest_runs",
        ["strategy_name"],
        unique=False,
    )
    op.create_index("ix_backtest_runs_status", "backtest_runs", ["status"], unique=False)
    op.create_index(
        "ix_backtest_runs_created_at",
        "backtest_runs",
        ["created_at"],
        unique=False,
    )

    op.create_table(
        "backtest_trades",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("side", sa.String(length=16), nullable=False),
        sa.Column("entry_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("entry_price", sa.Numeric(24, 10), nullable=False),
        sa.Column("exit_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("exit_price", sa.Numeric(24, 10), nullable=False),
        sa.Column("quantity", sa.Numeric(32, 12), nullable=False),
        sa.Column("notional", sa.Numeric(32, 10), nullable=False),
        sa.Column("fee", sa.Numeric(24, 10), nullable=False),
        sa.Column("slippage", sa.Numeric(24, 10), nullable=False),
        sa.Column("pnl", sa.Numeric(32, 10), nullable=False),
        sa.Column("pnl_pct", sa.Numeric(12, 6), nullable=False),
        sa.Column("holding_period_bars", sa.Integer(), nullable=False),
        sa.Column("exit_reason", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_backtest_trades_run_id", "backtest_trades", ["run_id"], unique=False)
    op.create_index("ix_backtest_trades_symbol", "backtest_trades", ["symbol"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_backtest_trades_symbol", table_name="backtest_trades")
    op.drop_index("ix_backtest_trades_run_id", table_name="backtest_trades")
    op.drop_table("backtest_trades")

    op.drop_index("ix_backtest_runs_created_at", table_name="backtest_runs")
    op.drop_index("ix_backtest_runs_status", table_name="backtest_runs")
    op.drop_index("ix_backtest_runs_strategy_name", table_name="backtest_runs")
    op.drop_index("ix_backtest_runs_timeframe", table_name="backtest_runs")
    op.drop_index("ix_backtest_runs_symbol", table_name="backtest_runs")
    op.drop_index("ix_backtest_runs_run_id", table_name="backtest_runs")
    op.drop_table("backtest_runs")
