from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app


def test_system_health_live_version(db_session: Session) -> None:
    app.dependency_overrides[get_db] = _override(db_session)
    try:
        client = TestClient(app)
        assert client.get("/system/health").status_code == 200
        assert client.get("/system/live").json() == {"status": "alive"}
        version = client.get("/system/version").json()
        assert version["service"]
        assert version["version"]
    finally:
        app.dependency_overrides.clear()


def test_system_ready_checks_database(db_session: Session) -> None:
    app.dependency_overrides[get_db] = _override(db_session)
    try:
        response = TestClient(app).get("/system/ready")
        assert response.status_code == 200
        body = response.json()
        assert body["checks"]["database"] == "ok"
        assert body["status"] in {"ready", "not_ready"}
    finally:
        app.dependency_overrides.clear()


def _override(db_session: Session):
    def dependency() -> Generator[Session, None, None]:
        yield db_session

    return dependency

