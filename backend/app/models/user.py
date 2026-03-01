"""
User model — stores account info, authentication credentials, and style profile.
"""

from sqlalchemy import Column, String, Integer
from app.database import Base
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    gender = Column(String(20), nullable=True)        # male, female, non-binary
    body_type = Column(String(30), nullable=True)      # slim, athletic, average, plus-size
    style_preference = Column(String(50), nullable=True)  # casual, formal, streetwear, bohemian, minimalist
