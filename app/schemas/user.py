"""
User schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for user creation"""
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    email: EmailStr
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for token response with user data"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
