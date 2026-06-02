"""Add Phase 7 paper trading tables.

Revision ID: 0006_add_paper_trading_tables
Revises: 0005_add_backtesting_tables
Create Date: 2026-05-27 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

revision: str = "0006_add_paper_trading_tables"
down_revision: str | None = "0005_add_backtesting_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    from alembic import op as alembic_op

    alembic_op.create_table(
        "paper_accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("initial_balance", sa.Numeric(24, 8), nullable=False),
        sa.Column("cash_balance", sa.Numeric(24, 8), nullable=False),
        sa.Column("equity", sa.Numeric(24, 8), nullable=False),
        sa.Column("realized_pnl", sa.Numeric(24, 8), nullable=False),
        sa.Column("unrealized_pnl", sa.Numeric(24, 8), nullable=False),
        sa.Column("total_fees", sa.Numeric(24, 8), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_id"),
    )
    alembic_op.create_index("ix_paper_accounts_account_id", "paper_accounts", ["account_id"])
    alembic_op.create_index("ix_paper_accounts_status", "paper_accounts", ["status"])
    alembic_op.create_index("ix_paper_accounts_created_at", "paper_accounts", ["created_at"])

    alembic_op.create_table(
        "paper_orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.String(length=64), nullable=False),
        sa.Column("account_id", sa.String(length=64), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("timeframe", sa.String(length=16), nullable=False),
        sa.Column("side", sa.String(length=16), nullable=False),
        sa.Column("order_type", sa.String(length=32), nullable=False),
        sa.Column("quantity", sa.Numeric(32, 12), nullable=True),
        sa.Column("notional", sa.Numeric(32, 10), nullable=False),
        sa.Column("requested_price", sa.Numeric(24, 10), nullable=True),
        sa.Column("filled_price", sa.Numeric(24, 10), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=True),
        sa.Column("signal_id", sa.String(length=64), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("fee", sa.Numeric(24, 10), nullable=True),
        sa.Column("slippage", sa.Numeric(24, 10), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("filled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_id"),
    )
    for column in ("order_id", "account_id", "symbol", "status", "created_at"):
        alembic_op.create_index(f"ix_paper_orders_{column}", "paper_orders", [column])

    alembic_op.create_table(
        "paper_positions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.String(length=64), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("quantity", sa.Numeric(32, 12), nullable=False),
        sa.Column("average_entry_price", sa.Numeric(24, 10), nullable=False),
        sa.Column("current_price", sa.Numeric(24, 10), nullable=False),
        sa.Column("market_value", sa.Numeric(32, 10), nullable=False),
        sa.Column("unrealized_pnl", sa.Numeric(32, 10), nullable=False),
        sa.Column("unrealized_pnl_pct", sa.Numeric(12, 6), nullable=False),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("account_id", "symbol", "status"):
        alembic_op.create_index(f"ix_paper_positions_{column}", "paper_positions", [column])

    with alembic_op.batch_alter_table("paper_trades") as batch_op:
        batch_op.add_column(sa.Column("trade_id", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("account_id", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("quantity", sa.Numeric(32, 12), nullable=True))
        batch_op.add_column(sa.Column("notional", sa.Numeric(32, 10), nullable=True))
        batch_op.add_column(sa.Column("fee", sa.Numeric(24, 10), nullable=True))
        batch_op.add_column(sa.Column("slippage", sa.Numeric(24, 10), nullable=True))
        batch_op.add_column(sa.Column("realized_pnl", sa.Numeric(32, 10), nullable=True))
        batch_op.add_column(sa.Column("realized_pnl_pct", sa.Numeric(12, 6), nullable=True))
        batch_op.add_column(sa.Column("source", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("exit_reason", sa.String(length=64), nullable=True))
        batch_op.alter_column("size", existing_type=sa.Numeric(32, 10), nullable=True)
        batch_op.alter_column("strategy_name", existing_type=sa.String(length=128), nullable=True)
    alembic_op.create_index("ix_paper_trades_trade_id", "paper_trades", ["trade_id"], unique=True)
    alembic_op.create_index("ix_paper_trades_account_id", "paper_trades", ["account_id"])

    alembic_op.create_table(
        "paper_equity_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.String(length=64), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cash_balance", sa.Numeric(24, 8), nullable=False),
        sa.Column("equity", sa.Numeric(24, 8), nullable=False),
        sa.Column("realized_pnl", sa.Numeric(24, 8), nullable=False),
        sa.Column("unrealized_pnl", sa.Numeric(24, 8), nullable=False),
        sa.Column("total_fees", sa.Numeric(24, 8), nullable=False),
        sa.Column("open_positions_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    alembic_op.create_index("ix_paper_equity_snapshots_account_id", "paper_equity_snapshots", ["account_id"])
    alembic_op.create_index("ix_paper_equity_snapshots_timestamp", "paper_equity_snapshots", ["timestamp"])


def downgrade() -> None:
    from alembic import op as alembic_op

    alembic_op.drop_index("ix_paper_equity_snapshots_timestamp", table_name="paper_equity_snapshots")
    alembic_op.drop_index("ix_paper_equity_snapshots_account_id", table_name="paper_equity_snapshots")
    alembic_op.drop_table("paper_equity_snapshots")
    alembic_op.drop_index("ix_paper_trades_account_id", table_name="paper_trades")
    alembic_op.drop_index("ix_paper_trades_trade_id", table_name="paper_trades")
    with alembic_op.batch_alter_table("paper_trades") as batch_op:
        batch_op.drop_column("exit_reason")
        batch_op.drop_column("source")
        batch_op.drop_column("realized_pnl_pct")
        batch_op.drop_column("realized_pnl")
        batch_op.drop_column("slippage")
        batch_op.drop_column("fee")
        batch_op.drop_column("notional")
        batch_op.drop_column("quantity")
        batch_op.drop_column("account_id")
        batch_op.drop_column("trade_id")
    alembic_op.drop_table("paper_positions")
    alembic_op.drop_table("paper_orders")
    alembic_op.drop_table("paper_accounts")
