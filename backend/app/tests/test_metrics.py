from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.main import app
from app.observability.metrics import metrics_registry


def test_metrics_endpoint_returns_prometheus_text(db_session: Session) -> None:
    app.dependency_overrides[get_db] = _override(db_session)
    metrics_registry.reset()
    try:
        client = TestClient(app)
        client.get("/health")
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "http_requests_total" in response.text
    finally:
        app.dependency_overrides.clear()


def test_metrics_endpoint_can_be_disabled(db_session: Session, monkeypatch) -> None:
    app.dependency_overrides[get_db] = _override(db_session)
    monkeypatch.setattr(settings, "ENABLE_METRICS", False)
    try:
        response = TestClient(app).get("/metrics")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


def _override(db_session: Session):
    def dependency() -> Generator[Session, None, None]:
        yield db_session

    return dependency

