from __future__ import annotations

from typing import Any

from app.paper_trading.broker import PaperBroker
from app.paper_trading.positions import PaperPositionManager
from app.services.signal_service import SignalService

PAPER_EXECUTION_DISCLAIMER = (
    "This is a research-only simulated paper trading action. No real order was placed."
)


class SignalPaperExecutor:
    def __init__(
        self,
        signal_service: SignalService,
        paper_broker: PaperBroker,
        settings: Any,
    ) -> None:
        self.signal_service = signal_service
        self.paper_broker = paper_broker
        self.settings = settings
        self.position_manager = PaperPositionManager(paper_broker.db_session)

    def evaluate_signal_for_paper_trade(
        self,
        account_id: str,
        symbol: str,
        timeframe: str,
        limit: int,
    ) -> dict[str, Any]:
        if not self.settings.ENABLE_SIGNAL_TO_PAPER_TRADE:
            return {
                "enabled": False,
                "message": "Signal-to-paper-trade simulation is disabled.",
                "disclaimer": PAPER_EXECUTION_DISCLAIMER,
            }
        signal = self.signal_service.generate_latest_signal(symbol, timeframe, limit)
        position = self.position_manager.get_position(account_id, symbol)
        score = signal["scores"]["overall_signal_score"]
        risk_level = signal["risk_level"]
        direction = signal["signal_direction"]
        if (
            score >= 75
            and direction in {"bullish", "mixed"}
            and risk_level not in {"high", "extreme"}
            and position is None
        ):
            account = self.paper_broker.account_manager.get_account(account_id)
            if account is None:
                raise ValueError("Paper account not found.")
            notional = min(
                account["equity"] * 0.10,
                account["equity"] * self.settings.PAPER_MAX_POSITION_PCT,
            )
            order = self.paper_broker.submit_order(
                {
                    "account_id": account_id,
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "side": "buy",
                    "order_type": "market",
                    "notional": notional,
                    "source": "signal_engine",
                    "reason": "Research-only signal simulation triggered by deterministic score.",
                }
            )
            return {
                "enabled": True,
                "signal": signal,
                "action_taken": "paper_order_submitted",
                "order": order,
                "reason": "Deterministic signal met the research-only simulated entry rule.",
                "disclaimer": PAPER_EXECUTION_DISCLAIMER,
            }
        if position and (direction == "bearish" or risk_level in {"high", "extreme"}):
            order = self.paper_broker.submit_order(
                {
                    "account_id": account_id,
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "side": "sell",
                    "order_type": "market",
                    "notional": position["market_value"],
                    "source": "signal_engine",
                    "reason": "Research-only signal simulation reduced an existing virtual position.",
                }
            )
            return {
                "enabled": True,
                "signal": signal,
                "action_taken": "paper_order_submitted",
                "order": order,
                "reason": "Deterministic signal met the research-only simulated exit rule.",
                "disclaimer": PAPER_EXECUTION_DISCLAIMER,
            }
        return {
            "enabled": True,
            "signal": signal,
            "action_taken": "no_action",
            "order": None,
            "reason": "Deterministic paper simulation rules did not trigger.",
            "disclaimer": PAPER_EXECUTION_DISCLAIMER,
        }
