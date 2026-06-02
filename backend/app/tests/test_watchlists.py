from sqlalchemy.orm import Session

from app.db.models import Workspace
from app.services.user_service import UserService
from app.services.watchlist_service import WatchlistService


def test_watchlist_crud_and_plan_limit(db_session: Session) -> None:
    user = UserService(db_session).register_user("watch@example.com", "Password123", "Watch")
    workspace_id = user["default_workspace_id"]
    assert workspace_id is not None
    service = WatchlistService(db_session)

    watchlist = service.create_watchlist(workspace_id, user["user_id"], "Layer 1")
    watchlist = service.add_symbol(workspace_id, watchlist["watchlist_id"], "avax/usdt", user["user_id"])
    assert watchlist["symbols"][0]["symbol"] == "AVAX/USDT"

    reordered = service.reorder_symbols(workspace_id, watchlist["watchlist_id"], ["AVAX/USDT"])
    assert reordered["symbols"][0]["display_order"] == 0
    removed = service.remove_symbol(workspace_id, watchlist["watchlist_id"], "AVAX/USDT")
    assert removed["symbols"] == []

    workspace = db_session.query(Workspace).filter_by(workspace_id=workspace_id).one()
    workspace.plan = "free"
    db_session.commit()
    limited = service.create_watchlist(workspace_id, user["user_id"], "Limit Test")
    for index in range(7):
        service.add_symbol(workspace_id, limited["watchlist_id"], f"T{index}/USDT", user["user_id"])
    try:
        service.add_symbol(workspace_id, limited["watchlist_id"], "OVER/USDT", user["user_id"])
    except PermissionError:
        assert True
    else:
        raise AssertionError("Watchlist symbol limit should be enforced.")
