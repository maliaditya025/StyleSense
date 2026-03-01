"""
Outfits router — generate outfit recommendations and get styling tips.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.clothing import Clothing
from app.models.outfit import Outfit
from app.schemas.outfit import (
    OutfitResponse, OutfitItemResponse, GenerateOutfitsRequest, StylingTipResponse,
)
from app.services.auth_service import get_current_user
from app.ai.recommender import generate_outfit_recommendations
from app.ai.stylist import generate_styling_tips

router = APIRouter(tags=["Outfits"])


@router.post("/generate-outfits", response_model=List[OutfitResponse])
async def generate_outfits(
    payload: GenerateOutfitsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate top 3 outfit recommendations from the user's closet.
    Uses AI scoring based on color harmony, gender, body type, and occasion.
    """
    # Fetch all user's clothing
    clothes = db.query(Clothing).filter(Clothing.user_id == current_user.id).all()

    if len(clothes) < 2:
        raise HTTPException(
            status_code=400,
            detail="You need at least 2 clothing items in your closet to generate outfits",
        )

    # Build user profile dict for the AI engine
    user_profile = {
        "gender": current_user.gender or "unspecified",
        "body_type": current_user.body_type or "average",
        "style_preference": current_user.style_preference or "casual",
    }

    # Convert clothing to dicts for the recommendation engine
    clothes_data = [
        {
            "id": c.id,
            "category": c.category,
            "primary_color": c.primary_color,
            "secondary_color": c.secondary_color,
            "color_name": c.color_name,
            "image_url": c.image_url,
        }
        for c in clothes
    ]

    # Run the recommendation engine
    recommendations = generate_outfit_recommendations(
        clothes=clothes_data,
        user_profile=user_profile,
        occasion=payload.occasion,
        top_n=3,
    )

    # Save outfits to database and build response
    results = []
    for rec in recommendations:
        outfit = Outfit(
            user_id=current_user.id,
            items=[item["id"] for item in rec["items"]],
            score=rec["score"],
            occasion=payload.occasion,
            tips=rec.get("tips", []),
        )
        db.add(outfit)
        db.commit()
        db.refresh(outfit)

        # Build the full response with item details
        outfit_items = [
            OutfitItemResponse(
                id=item["id"],
                category=item["category"],
                primary_color=item["primary_color"],
                secondary_color=item.get("secondary_color"),
                color_name=item.get("color_name"),
                image_url=item["image_url"],
            )
            for item in rec["items"]
        ]

        results.append(OutfitResponse(
            id=outfit.id,
            user_id=outfit.user_id,
            items=outfit_items,
            score=outfit.score,
            occasion=outfit.occasion,
            tips=outfit.tips,
            created_at=outfit.created_at,
        ))

    return results


@router.get("/styling-tips", response_model=StylingTipResponse)
async def get_styling_tips_endpoint(
    outfit_id: str = Query(..., description="ID of the outfit to get tips for"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed styling tips for a specific outfit.
    Includes accessory suggestions, footwear, do's & don'ts, and grooming tips.
    """
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user.id,
    ).first()

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    # Fetch the actual clothing items
    clothes = db.query(Clothing).filter(Clothing.id.in_(outfit.items)).all()
    clothes_data = [
        {
            "category": c.category,
            "primary_color": c.primary_color,
            "color_name": c.color_name,
        }
        for c in clothes
    ]

    user_profile = {
        "gender": current_user.gender or "unspecified",
        "body_type": current_user.body_type or "average",
        "style_preference": current_user.style_preference or "casual",
    }

    tips = generate_styling_tips(
        outfit_items=clothes_data,
        occasion=outfit.occasion or "casual",
        user_profile=user_profile,
    )

    return StylingTipResponse(
        outfit_id=outfit_id,
        **tips,
    )


@router.get("/outfits", response_model=List[OutfitResponse])
async def get_saved_outfits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all previously generated outfits for the current user."""
    outfits = db.query(Outfit).filter(
        Outfit.user_id == current_user.id
    ).order_by(Outfit.created_at.desc()).limit(20).all()

    results = []
    for outfit in outfits:
        clothes = db.query(Clothing).filter(Clothing.id.in_(outfit.items)).all()
        outfit_items = [
            OutfitItemResponse(
                id=c.id,
                category=c.category,
                primary_color=c.primary_color,
                secondary_color=c.secondary_color,
                color_name=c.color_name,
                image_url=c.image_url,
            )
            for c in clothes
        ]

        results.append(OutfitResponse(
            id=outfit.id,
            user_id=outfit.user_id,
            items=outfit_items,
            score=outfit.score,
            occasion=outfit.occasion,
            tips=outfit.tips,
            created_at=outfit.created_at,
        ))

    return results
