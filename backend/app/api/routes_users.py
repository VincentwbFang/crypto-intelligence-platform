from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.db.session import get_db
from app.schemas.auth import AuthUserResponse
from app.schemas.users import (
    UserPreferenceResponse,
    UserPreferenceUpdateRequest,
    UserProfileUpdateRequest,
)
from app.services.user_preferences_service import UserPreferencesService
from app.services.user_service import UserService

router = APIRouter(tags=["users"])


@router.get("/me", response_model=AuthUserResponse)
def get_profile(current_user: dict = Depends(get_current_active_user)) -> AuthUserResponse:
    return AuthUserResponse(**current_user)


@router.patch("/me", response_model=AuthUserResponse)
def update_profile(
    request: UserProfileUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> AuthUserResponse:
    return AuthUserResponse(
        **UserService(db).update_user_profile(
            current_user["user_id"],
            request.model_dump(exclude_unset=True),
        )
    )


@router.get("/me/preferences", response_model=UserPreferenceResponse)
def get_preferences(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> UserPreferenceResponse:
    return UserPreferenceResponse(
        **UserPreferencesService(db).get_preferences(current_user["user_id"])
    )


@router.patch("/me/preferences", response_model=UserPreferenceResponse)
def update_preferences(
    request: UserPreferenceUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> UserPreferenceResponse:
    return UserPreferenceResponse(
        **UserPreferencesService(db).update_preferences(
            current_user["user_id"],
            request.model_dump(exclude_unset=True),
        )
    )
