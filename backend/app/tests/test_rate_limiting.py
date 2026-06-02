from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.security.rate_limit import rate_limiter


def test_rate_limit_can_return_429(monkeypatch) -> None:
    monkeypatch.setattr(settings, "ENABLE_RATE_LIMITING", True)
    monkeypatch.setattr(settings, "RATE_LIMIT_AUTH", "1/minute")
    rate_limiter.reset()
    client = TestClient(app)
    assert client.post("/auth/refresh", json={}).status_code == 422
    response = client.post("/auth/refresh", json={})
    assert response.status_code == 429
    assert response.json()["error"]["type"] == "rate_limit_exceeded"


def test_health_is_not_rate_limited(monkeypatch) -> None:
    monkeypatch.setattr(settings, "ENABLE_RATE_LIMITING", True)
    monkeypatch.setattr(settings, "RATE_LIMIT_DEFAULT", "1/minute")
    rate_limiter.reset()
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    assert client.get("/health").status_code == 200
