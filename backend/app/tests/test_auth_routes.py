from collections.abc import Generator

from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.main import app


def test_auth_routes_register_login_me_refresh_logout(db_session: Session) -> None:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        client = TestClient(app)
        register = client.post(
            "/auth/register",
            json={
                "email": "route@example.com",
                "password": "Password123",
                "full_name": "Route User",
            },
        )
        assert register.status_code == 200
        data = register.json()
        assert data["access_token"]
        assert data["refresh_token"]
        assert data["workspace"]["workspace_id"]

        login = client.post(
            "/auth/login",
            json={"email": "route@example.com", "password": "Password123"},
        )
        assert login.status_code == 200
        access_token = login.json()["access_token"]
        refresh_token = login.json()["refresh_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        me = client.get("/auth/me", headers=headers)
        assert me.status_code == 200
        assert me.json()["user"]["email"] == "route@example.com"

        refreshed = client.post("/auth/refresh", json={"refresh_token": refresh_token})
        assert refreshed.status_code == 200
        logout = client.post("/auth/logout", json={"refresh_token": refresh_token})
        assert logout.status_code == 200
    finally:
        app.dependency_overrides.clear()


def test_product_routes_require_auth_when_enabled(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    monkeypatch.setattr(settings, "ENABLE_AUTH", True)
    app.dependency_overrides[get_db] = override_get_db
    try:
        client = TestClient(app)
        response = client.get("/alerts")
        assert response.status_code == 401
        assert response.json()["error"]["message"] == "Authentication required."
    finally:
        app.dependency_overrides.clear()


def test_product_routes_accept_bearer_token_when_auth_enabled(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    monkeypatch.setattr(settings, "ENABLE_AUTH", True)
    app.dependency_overrides[get_db] = override_get_db
    try:
        client = TestClient(app)
        register = client.post(
            "/auth/register",
            json={
                "email": "protected@example.com",
                "password": "Password123",
                "full_name": "Protected User",
            },
        )
        assert register.status_code == 200
        headers = {"Authorization": f"Bearer {register.json()['access_token']}"}
        alerts = client.get("/alerts", headers=headers)
        assert alerts.status_code == 200
        assert alerts.json()["data"] == []
    finally:
        app.dependency_overrides.clear()
