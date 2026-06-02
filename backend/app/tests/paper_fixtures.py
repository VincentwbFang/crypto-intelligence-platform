from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.db.models import OHLCV
from app.schemas.paper_trading import PaperAccountCreateRequest, PaperOrderCreateRequest
from app.services.paper_trading_service import PaperTradingService


def seed_latest_ohlcv(
    db_session: Session,
    symbol: str = "BTC/USDT",
    timeframe: str = "1h",
    close: float = 100.0,
    count: int = 3,
) -> None:
    start = datetime(2026, 5, 27, tzinfo=UTC)
    for index in range(count):
        price = close + index
        db_session.add(
            OHLCV(
                exchange="binance",
                symbol=symbol,
                timeframe=timeframe,
                timestamp=start + timedelta(hours=index),
                open=Decimal(str(price - 1)),
                high=Decimal(str(price + 2)),
                low=Decimal(str(price - 2)),
                close=Decimal(str(price)),
                volume=Decimal("1000"),
            )
        )
    db_session.commit()


def create_account(db_session: Session, balance: float = 10_000) -> dict:
    return PaperTradingService(db_session).create_account(
        PaperAccountCreateRequest(name="Test Paper Account", initial_balance=balance)
    )


def buy_order(account_id: str, notional: float = 500) -> PaperOrderCreateRequest:
    return PaperOrderCreateRequest(
        account_id=account_id,
        symbol="BTC/USDT",
        timeframe="1h",
        side="buy",
        order_type="market",
        notional=notional,
        reason="Test simulated order",
    )


def sell_order(account_id: str, notional: float = 250) -> PaperOrderCreateRequest:
    return PaperOrderCreateRequest(
        account_id=account_id,
        symbol="BTC/USDT",
        timeframe="1h",
        side="sell",
        order_type="market",
        notional=notional,
        reason="Test simulated reduction",
    )
