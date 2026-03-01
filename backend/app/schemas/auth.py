"""
Pydantic schemas for authentication requests and responses.
"""

from typing import Optional
from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, examples=["John Doe"])
    email: str = Field(..., min_length=5, max_length=255, examples=["john@example.com"])
    password: str = Field(..., min_length=6, max_length=128, examples=["SecurePass123"])


class LoginRequest(BaseModel):
    email: str = Field(..., examples=["john@example.com"])
    password: str = Field(..., examples=["SecurePass123"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    gender: Optional[str] = None
    body_type: Optional[str] = None
    style_preference: Optional[str] = None

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ProfileUpdateRequest(BaseModel):
    gender: Optional[str] = Field(None, examples=["male"])
    body_type: Optional[str] = Field(None, examples=["athletic"])
    style_preference: Optional[str] = Field(None, examples=["casual"])
    name: Optional[str] = Field(None, min_length=2, max_length=100)
