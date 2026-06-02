from __future__ import annotations

from pydantic import BaseModel


class UsageSummaryResponse(BaseModel):
    workspace_id: str
    usage: dict[str, int]
    plan: str | None = None
    limits: dict | None = None


class PlanLimitsResponse(BaseModel):
    workspace_id: str
    plan: str
    limits: dict
