from fastapi.testclient import TestClient

from app.main import app


def test_system_routes_do_not_expose_secrets() -> None:
    response = TestClient(app).get("/system/version")
    assert response.status_code == 200
    body = response.text.lower()
    assert "jwt_secret" not in body
    assert "deepseek_api_key" not in body
    assert "password" not in body

