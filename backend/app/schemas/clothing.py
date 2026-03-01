"""
Pydantic schemas for clothing data.
"""

from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class ClothingResponse(BaseModel):
    id: str
    user_id: str
    category: str
    confidence_score: Optional[float] = None
    primary_color: str
    secondary_color: Optional[str] = None
    color_name: Optional[str] = None
    image_url: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClothingCreate(BaseModel):
    """Used internally after AI processing — not exposed directly to API."""
    category: str
    primary_color: str
    secondary_color: Optional[str] = None
    color_name: Optional[str] = None
    image_url: str
