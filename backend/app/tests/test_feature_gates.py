from sqlalchemy.orm import Session

from app.db.models import Workspace
from app.services.user_service import UserService
from app.subscriptions.feature_gates import FeatureGateService


def test_feature_gate_plan_limits(db_session: Session) -> None:
    user = UserService(db_session).register_user("gate@example.com", "Password123", "Gate")
    workspace_id = user["default_workspace_id"]
    assert workspace_id is not None
    gate = FeatureGateService(db_session)
    assert gate.get_workspace_plan(workspace_id) == "free"
    assert gate.check_feature(workspace_id, "alert_scheduler")["allowed"] is False

    workspace = db_session.query(Workspace).filter_by(workspace_id=workspace_id).one()
    workspace.plan = "pro"
    db_session.commit()
    assert gate.check_feature(workspace_id, "alert_scheduler")["allowed"] is True
