from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.main import app
from app.tests.paper_fixtures import seed_latest_ohlcv


def test_paper_trading_routes(db_session: Session) -> None:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    seed_latest_ohlcv(db_session)
    try:
        client = TestClient(app)
        account_response = client.post(
            "/paper/accounts",
            json={"name": "Route Paper Account", "initial_balance": 10000},
        )
        assert account_response.status_code == 200
        account_id = account_response.json()["account_id"]

        assert client.get("/paper/accounts").status_code == 200
        order_response = client.post(
            "/paper/orders",
            json={
                "account_id": account_id,
                "symbol": "BTC/USDT",
                "timeframe": "1h",
                "side": "buy",
                "order_type": "market",
                "notional": 500,
            },
        )
        assert order_response.status_code == 200
        assert order_response.json()["status"] == "filled"

        assert client.get(f"/paper/accounts/{account_id}/positions").status_code == 200
        assert client.get(f"/paper/accounts/{account_id}/trades").status_code == 200
        assert client.get(f"/paper/accounts/{account_id}/portfolio").status_code == 200
        assert client.get(f"/paper/accounts/{account_id}/performance").status_code == 200
        signal_response = client.post(
            f"/paper/accounts/{account_id}/signal-execution",
            json={"symbol": "BTC/USDT", "timeframe": "1h", "limit": 200},
        )
        assert signal_response.status_code == 200
        assert signal_response.json()["enabled"] is False
        explain_response = client.get(f"/paper/accounts/{account_id}/explain")
        assert explain_response.status_code == 200
        assert explain_response.json()["enabled"] is False
    finally:
        app.dependency_overrides.clear()
