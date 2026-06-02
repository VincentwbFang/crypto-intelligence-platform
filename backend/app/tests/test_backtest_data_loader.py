from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.backtesting.data_loader import BacktestDataLoader, validate_ohlcv_dataframe
from app.db.base import Base
from app.db.models import OHLCV
from app.tests.backtest_fixtures import seed_ohlcv


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_loads_ohlcv_sorted_ascending(db_session: Session) -> None:
    seed_ohlcv(db_session, count=3)
    loader = BacktestDataLoader(db_session)
    rows = loader.load_ohlcv(
        "BTC/USDT",
        "1h",
        datetime(2025, 1, 1, tzinfo=UTC),
        datetime(2025, 1, 2, tzinfo=UTC),
    )
    assert rows[0]["timestamp"] < rows[-1]["timestamp"]


def test_returns_empty_result_if_no_data(db_session: Session) -> None:
    loader = BacktestDataLoader(db_session)
    rows = loader.load_ohlcv(
        "BTC/USDT",
        "1h",
        datetime(2025, 1, 1, tzinfo=UTC),
        datetime(2025, 1, 2, tzinfo=UTC),
    )
    assert rows == []


def test_deduplicates_timestamps(db_session: Session) -> None:
    timestamp = datetime(2025, 1, 1, tzinfo=UTC)
    for exchange in ("binance", "coinbase"):
        db_session.add(
            OHLCV(
                exchange=exchange,
                symbol="BTC/USDT",
                timeframe="1h",
                timestamp=timestamp,
                open=Decimal("100"),
                high=Decimal("101"),
                low=Decimal("99"),
                close=Decimal("100"),
                volume=Decimal("1000"),
            )
        )
    db_session.commit()
    rows = BacktestDataLoader(db_session).load_ohlcv(
        "BTC/USDT",
        "1h",
        timestamp - timedelta(hours=1),
        timestamp + timedelta(hours=1),
    )
    assert len(rows) == 1


def test_validates_required_columns() -> None:
    with pytest.raises(ValueError):
        validate_ohlcv_dataframe(__import__("pandas").DataFrame({"close": [1]}))
