from sqlalchemy.orm import Session

from app.core.config import settings
from app.paper_trading.execution import SimulatedExecutionEngine
from app.tests.paper_fixtures import seed_latest_ohlcv


def test_latest_price_loads_from_stored_ohlcv(db_session: Session) -> None:
    seed_latest_ohlcv(db_session, close=100)

    price = SimulatedExecutionEngine(db_session, settings).get_latest_price("BTC/USDT", "1h")

    assert price["latest_close"] == 102.0


def test_slippage_and_fee_calculation(db_session: Session) -> None:
    seed_latest_ohlcv(db_session, close=100)
    engine = SimulatedExecutionEngine(db_session, settings)

    buy = engine.simulate_market_fill(
        {"symbol": "BTC/USDT", "timeframe": "1h", "side": "buy", "notional": 1000}
    )
    sell = engine.simulate_market_fill(
        {"symbol": "BTC/USDT", "timeframe": "1h", "side": "sell", "notional": 1000}
    )

    assert buy["filled_price"] > buy["requested_price"]
    assert sell["filled_price"] < sell["requested_price"]
    assert buy["fee"] == 1.0
