"""
Pydantic schemas for outfit data.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class OutfitItemResponse(BaseModel):
    """A clothing item within an outfit."""
    id: str
    category: str
    primary_color: str
    secondary_color: Optional[str] = None
    color_name: Optional[str] = None
    image_url: str


class OutfitResponse(BaseModel):
    id: str
    user_id: str
    items: List[OutfitItemResponse]
    score: float
    occasion: Optional[str] = None
    tips: Optional[List[str]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GenerateOutfitsRequest(BaseModel):
    occasion: str = Field("casual", examples=["casual", "formal", "party", "work", "date"])


class StylingTipResponse(BaseModel):
    outfit_id: str
    tips: List[str]
    accessories: List[str]
    footwear: List[str]
    dos: List[str]
    donts: List[str]
    grooming: List[str]
