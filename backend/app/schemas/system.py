from __future__ import annotations

from pydantic import BaseModel, Field


class SystemHealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str


class SystemLiveResponse(BaseModel):
    status: str


class SystemReadyResponse(BaseModel):
    status: str
    checks: dict[str, str] = Field(default_factory=dict)


class SystemVersionResponse(BaseModel):
    version: str
    service: str
    environment: str
