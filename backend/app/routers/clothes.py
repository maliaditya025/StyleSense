"""
Clothes router — upload clothing images and view virtual closet.
Upload triggers AI detection and color extraction automatically.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.clothing import Clothing
from app.schemas.clothing import ClothingResponse
from app.services.auth_service import get_current_user
from app.utils.file_upload import save_upload_file
from app.ai.detector import detect_clothing_with_confidence
from app.ai.color_extractor import extract_colors
import os
from app.config import get_settings

settings = get_settings()
router = APIRouter(tags=["Clothing"])

VALID_CATEGORIES = [
    "shirt", "t-shirt", "pants", "jeans", "shoes",
    "jacket", "dress", "accessories", "shorts", "skirt",
]


@router.post("/upload-clothes", response_model=ClothingResponse, status_code=201)
async def upload_clothes(
    file: UploadFile = File(...),
    category_override: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload a clothing image. The CNN model will:
    1. Detect the clothing category with confidence score
    2. Extract dominant colors
    3. Save the item to the user's virtual closet

    If category_override is provided, it will be used instead of AI detection.
    """
    # Save file to disk
    image_url = await save_upload_file(file, current_user.id)

    # Get the absolute file path for AI processing
    file_path = os.path.join(settings.UPLOAD_DIR, current_user.id, os.path.basename(image_url))

    # Use override if provided, otherwise run CNN detection
    confidence = None
    if category_override and category_override.lower() in VALID_CATEGORIES:
        category = category_override.lower()
        confidence = 1.0  # Manual override = 100% confidence
    else:
        result = detect_clothing_with_confidence(file_path)
        category = result["category"]
        confidence = result.get("confidence")

    colors = extract_colors(file_path)

    # Create clothing record
    clothing = Clothing(
        user_id=current_user.id,
        category=category,
        confidence_score=confidence,
        primary_color=colors["primary"],
        secondary_color=colors.get("secondary"),
        color_name=colors.get("name"),
        image_url=image_url,
    )
    db.add(clothing)
    db.commit()
    db.refresh(clothing)

    return ClothingResponse.model_validate(clothing)


@router.get("/closet", response_model=List[ClothingResponse])
async def get_closet(
    category: Optional[str] = Query(None, description="Filter by category"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the user's virtual closet.
    Optionally filter by clothing category.
    """
    query = db.query(Clothing).filter(Clothing.user_id == current_user.id)

    if category:
        query = query.filter(Clothing.category == category.lower())

    items = query.order_by(Clothing.created_at.desc()).all()
    return [ClothingResponse.model_validate(item) for item in items]


@router.delete("/closet/{item_id}", status_code=204)
async def delete_clothing(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a clothing item from the closet."""
    item = db.query(Clothing).filter(
        Clothing.id == item_id,
        Clothing.user_id == current_user.id,
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Clothing item not found")

    # Delete the image file
    file_path = os.path.join(".", item.image_url.lstrip("/"))
    if os.path.exists(file_path):
        os.remove(file_path)

    db.delete(item)
    db.commit()
