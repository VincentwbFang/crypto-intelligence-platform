from __future__ import annotations

from decimal import Decimal
from typing import Any


class PaperRiskManager:
    def __init__(self, settings: Any) -> None:
        self.settings = settings

    def validate_order(
        self,
        account: dict[str, Any],
        order: dict[str, Any],
        positions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        reasons: list[str] = []
        current_position = self._find_position(order["symbol"], positions)
        for result in (
            self.check_no_leverage(order),
            self.check_no_shorting(order, current_position),
            self.check_max_position_size(account, order, current_position),
            self.check_cash_available(account, order),
            self.check_max_open_positions(account, positions, order),
            self.check_daily_loss_limit(account),
        ):
            reasons.extend(result["reasons"])
        return {"approved": not reasons, "reasons": reasons}

    def check_max_position_size(
        self,
        account: dict[str, Any],
        order: dict[str, Any],
        current_position: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if order["side"] != "buy":
            return {"approved": True, "reasons": []}
        max_notional = Decimal(str(account["equity"])) * Decimal(str(self.settings.PAPER_MAX_POSITION_PCT))
        current_value = Decimal(str((current_position or {}).get("market_value") or 0))
        proposed_value = current_value + Decimal(str(order["notional"]))
        if proposed_value > max_notional:
            return {
                "approved": False,
                "reasons": ["Simulated order exceeds the maximum position size limit."],
            }
        return {"approved": True, "reasons": []}

    def check_cash_available(self, account: dict[str, Any], order: dict[str, Any]) -> dict[str, Any]:
        if order["side"] != "buy":
            return {"approved": True, "reasons": []}
        notional = Decimal(str(order["notional"]))
        fee = notional * Decimal(str(self.settings.PAPER_DEFAULT_FEE_BPS)) / Decimal("10000")
        if Decimal(str(account["cash_balance"])) < notional + fee:
            return {"approved": False, "reasons": ["Virtual cash balance is insufficient."]}
        return {"approved": True, "reasons": []}

    def check_max_open_positions(
        self,
        account: dict[str, Any],
        positions: list[dict[str, Any]],
        order: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        del account
        if order and order.get("side") != "buy":
            return {"approved": True, "reasons": []}
        open_positions = [position for position in positions if position.get("status") == "open"]
        if order and self._find_position(str(order.get("symbol")), open_positions):
            return {"approved": True, "reasons": []}
        if len(open_positions) >= self.settings.PAPER_MAX_OPEN_POSITIONS:
            return {"approved": False, "reasons": ["Maximum open simulated positions reached."]}
        return {"approved": True, "reasons": []}

    def check_daily_loss_limit(self, account: dict[str, Any]) -> dict[str, Any]:
        initial_balance = Decimal(str(account["initial_balance"]))
        realized_pnl = Decimal(str(account["realized_pnl"]))
        max_loss = -initial_balance * Decimal(str(self.settings.PAPER_MAX_DAILY_LOSS_PCT))
        if realized_pnl <= max_loss:
            return {"approved": False, "reasons": ["Daily simulated loss limit has been reached."]}
        return {"approved": True, "reasons": []}

    def check_no_shorting(
        self,
        order: dict[str, Any],
        current_position: dict[str, Any] | None,
    ) -> dict[str, Any]:
        if self.settings.PAPER_ALLOW_SHORTING or order["side"] != "sell":
            return {"approved": True, "reasons": []}
        quantity = Decimal(str(order.get("quantity") or 0))
        current_quantity = Decimal(str((current_position or {}).get("quantity") or 0))
        tolerance = Decimal("0.00000001")
        if current_quantity <= 0 or (quantity > 0 and quantity - current_quantity > tolerance):
            return {"approved": False, "reasons": ["Shorting is disabled for paper trading."]}
        return {"approved": True, "reasons": []}

    def check_no_leverage(self, order: dict[str, Any]) -> dict[str, Any]:
        if self.settings.PAPER_ALLOW_LEVERAGE:
            return {"approved": True, "reasons": []}
        if float(order.get("leverage", 1) or 1) != 1:
            return {"approved": False, "reasons": ["Leverage is disabled for paper trading."]}
        return {"approved": True, "reasons": []}

    @staticmethod
    def _find_position(symbol: str, positions: list[dict[str, Any]]) -> dict[str, Any] | None:
        for position in positions:
            if position.get("symbol") == symbol and position.get("status") == "open":
                return position
        return None
