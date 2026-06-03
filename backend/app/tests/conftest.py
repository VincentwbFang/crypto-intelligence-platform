from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base


@pytest.fixture(autouse=True)
def disable_route_auth_for_legacy_api_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "ENABLE_AUTH", False)
    monkeypatch.setattr(settings, "JWT_SECRET_KEY", "phase-eight-test-secret")
    monkeypatch.setattr(settings, "ENABLE_RATE_LIMITING", False)
    monkeypatch.setattr(settings, "ENABLE_MARKET_DATA_SCHEDULER", False)
    monkeypatch.setattr(settings, "ENABLE_RELATIVE_STRENGTH_SCHEDULER", False)
    monkeypatch.setattr(settings, "ENABLE_NEWS_SCHEDULER", False)
    monkeypatch.setattr(settings, "NEWS_LLM_ENABLED", False)


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
