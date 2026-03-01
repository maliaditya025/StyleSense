"""
Profile router — manage user profile (gender, body type, style preferences).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserResponse, ProfileUpdateRequest
from app.services.auth_service import get_current_user

router = APIRouter(tags=["Profile"])


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get the current user's profile."""
    return UserResponse.model_validate(current_user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update profile fields (gender, body_type, style_preference, name).
    Only updates fields that are provided (non-None).
    """
    if payload.gender is not None:
        current_user.gender = payload.gender
    if payload.body_type is not None:
        current_user.body_type = payload.body_type
    if payload.style_preference is not None:
        current_user.style_preference = payload.style_preference
    if payload.name is not None:
        current_user.name = payload.name

    db.commit()
    db.refresh(current_user)

    return UserResponse.model_validate(current_user)
