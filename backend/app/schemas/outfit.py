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
    occasion: str = Field("casual", examples=["casual", "formal", "party", "work", "date", "vacation", "gym"])
    weather: Optional[str] = Field("", examples=["hot", "warm", "cold", "rainy"])
    time_of_day: Optional[str] = Field("", examples=["morning", "afternoon", "evening", "night"])
    location: Optional[str] = Field("", examples=["indoor", "outdoor"])


class StylingTipResponse(BaseModel):
    outfit_id: str
    tips: List[str]
    accessories: List[str]
    footwear: List[str]
    dos: List[str]
    donts: List[str]
    grooming: List[str]
