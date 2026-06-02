from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app


def test_request_id_generated_when_missing(db_session: Session) -> None:
    app.dependency_overrides[get_db] = _override(db_session)
    try:
        response = TestClient(app).get("/health")
        assert response.status_code == 200
        assert response.headers["X-Request-ID"]
    finally:
        app.dependency_overrides.clear()


def test_request_id_preserves_valid_incoming_value(db_session: Session) -> None:
    app.dependency_overrides[get_db] = _override(db_session)
    try:
        response = TestClient(app).get("/health", headers={"X-Request-ID": "req-123"})
        assert response.headers["X-Request-ID"] == "req-123"
    finally:
        app.dependency_overrides.clear()


def test_request_id_replaces_unsafe_long_value(db_session: Session) -> None:
    app.dependency_overrides[get_db] = _override(db_session)
    try:
        response = TestClient(app).get("/health", headers={"X-Request-ID": "x" * 300})
        assert response.headers["X-Request-ID"] != "x" * 300
        assert len(response.headers["X-Request-ID"]) <= 128
    finally:
        app.dependency_overrides.clear()


def _override(db_session: Session):
    def dependency() -> Generator[Session, None, None]:
        yield db_session

    return dependency

