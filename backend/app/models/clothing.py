"""
Clothing model — stores individual clothing items uploaded by users.
Each item has AI-detected category and extracted colors.
"""

from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Clothing(Base):
    __tablename__ = "clothing"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    category = Column(String(50), nullable=False)       # shirt, t-shirt, pants, jeans, shoes, jacket, dress, accessories
    confidence_score = Column(Float, nullable=True)      # CNN prediction confidence (0-1)
    primary_color = Column(String(30), nullable=False)   # hex color e.g. #FF5733
    secondary_color = Column(String(30), nullable=True)  # hex color
    color_name = Column(String(30), nullable=True)       # human-readable color name
    image_url = Column(String(500), nullable=False)      # relative path to uploaded image
    created_at = Column(DateTime, server_default=func.now())
