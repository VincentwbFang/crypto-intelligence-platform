from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import PaperAccount, PaperPosition
from app.paper_trading.serialization import to_float, to_iso

ACCOUNT_STATUSES = {"active", "paused", "closed"}


class PaperAccountManager:
    def __init__(
        self,
        db_session: Session,
        workspace_id: str | None = None,
        user_id: str | None = None,
    ) -> None:
        self.db_session = db_session
        self.workspace_id = workspace_id
        self.user_id = user_id

    def create_account(self, name: str, initial_balance: float) -> dict[str, Any]:
        if initial_balance <= 0:
            raise ValueError("initial_balance must be greater than zero.")
        account = PaperAccount(
            workspace_id=self.workspace_id,
            created_by_user_id=self.user_id,
            account_id=str(uuid4()),
            name=name,
            initial_balance=Decimal(str(initial_balance)),
            cash_balance=Decimal(str(initial_balance)),
            equity=Decimal(str(initial_balance)),
            realized_pnl=Decimal("0"),
            unrealized_pnl=Decimal("0"),
            total_fees=Decimal("0"),
            status="active",
        )
        self.db_session.add(account)
        self.db_session.commit()
        return self.to_dict(account)

    def get_account(self, account_id: str) -> dict[str, Any] | None:
        row = self.get_account_row(account_id)
        return self.to_dict(row) if row else None

    def get_account_row(self, account_id: str) -> PaperAccount | None:
        statement = select(PaperAccount).where(PaperAccount.account_id == account_id)
        if self.workspace_id:
            statement = statement.where(PaperAccount.workspace_id == self.workspace_id)
        return self.db_session.scalar(statement)

    def list_accounts(self, status: str | None = None) -> list[dict[str, Any]]:
        statement = select(PaperAccount).order_by(PaperAccount.created_at.desc())
        if self.workspace_id:
            statement = statement.where(PaperAccount.workspace_id == self.workspace_id)
        if status:
            statement = statement.where(PaperAccount.status == status)
        return [self.to_dict(row) for row in self.db_session.scalars(statement).all()]

    def pause_account(self, account_id: str) -> dict[str, Any]:
        return self._set_status(account_id, "paused")

    def activate_account(self, account_id: str) -> dict[str, Any]:
        return self._set_status(account_id, "active")

    def close_account(self, account_id: str) -> dict[str, Any]:
        return self._set_status(account_id, "closed")

    def update_account_equity(self, account_id: str) -> dict[str, Any]:
        account = self._require_account(account_id)
        statement = select(PaperPosition).where(
            PaperPosition.account_id == account_id,
            PaperPosition.status == "open",
        )
        if self.workspace_id:
            statement = statement.where(PaperPosition.workspace_id == self.workspace_id)
        positions = self.db_session.scalars(statement).all()
        unrealized = sum((position.unrealized_pnl for position in positions), Decimal("0"))
        market_value = sum((position.market_value for position in positions), Decimal("0"))
        account.unrealized_pnl = unrealized
        account.equity = account.cash_balance + market_value
        account.updated_at = datetime.now(UTC)
        self.db_session.commit()
        return self.to_dict(account)

    def _set_status(self, account_id: str, status: str) -> dict[str, Any]:
        if status not in ACCOUNT_STATUSES:
            raise ValueError("Invalid paper account status.")
        account = self._require_account(account_id)
        account.status = status
        account.updated_at = datetime.now(UTC)
        self.db_session.commit()
        return self.to_dict(account)

    def _require_account(self, account_id: str) -> PaperAccount:
        account = self.get_account_row(account_id)
        if account is None:
            raise ValueError("Paper account not found.")
        return account

    @staticmethod
    def to_dict(account: PaperAccount) -> dict[str, Any]:
        return {
            "id": account.id,
            "workspace_id": account.workspace_id,
            "created_by_user_id": account.created_by_user_id,
            "account_id": account.account_id,
            "name": account.name,
            "initial_balance": to_float(account.initial_balance),
            "cash_balance": to_float(account.cash_balance),
            "equity": to_float(account.equity),
            "realized_pnl": to_float(account.realized_pnl),
            "unrealized_pnl": to_float(account.unrealized_pnl),
            "total_fees": to_float(account.total_fees),
            "status": account.status,
            "created_at": to_iso(account.created_at),
            "updated_at": to_iso(account.updated_at),
        }
