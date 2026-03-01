"""
Outfit model — stores generated outfit combinations with scores.
Items are stored as JSON array of clothing IDs.
"""

from sqlalchemy import Column, String, Float, JSON, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Outfit(Base):
    __tablename__ = "outfits"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    items = Column(JSON, nullable=False)        # list of clothing IDs
    score = Column(Float, nullable=False)       # overall outfit score 0-100
    occasion = Column(String(50), nullable=True)  # casual, formal, party, work, date
    tips = Column(JSON, nullable=True)          # list of styling tip strings
    created_at = Column(DateTime, server_default=func.now())
