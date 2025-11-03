from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class ParticipantBase(BaseModel):
    """Base schema for Participant"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    address: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=50)


class ParticipantCreate(ParticipantBase):
    """Schema for creating a Participant"""
    pass


class ParticipantResponse(ParticipantBase):
    """Schema for Participant response"""
    id: int
    draw_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DrawBase(BaseModel):
    """Base schema for Draw"""
    status: Optional[str] = None
    draw_type: Optional[str] = None
    draw_date: Optional[datetime] = None
    require_address: bool = False
    require_phone: bool = False


class DrawCreate(BaseModel):
    """Schema for creating a Draw with participants"""
    draw_date: Optional[datetime] = Field(
        None,
        description="Date and time of the draw (must be in the future if provided)"
    )
    require_address: bool = False
    require_phone: bool = False
    participants: List[ParticipantCreate] = Field(
        ...,
        min_items=2,
        description="List of participants (minimum 2 required)"
    )
    
    @field_validator('draw_date')
    @classmethod
    def validate_draw_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate that draw_date is in the future if provided"""
        if v is not None:
            from datetime import timezone
            now = datetime.now(timezone.utc)
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)
            if v <= now:
                raise ValueError("draw_date must be in the future")
        return v


class DrawResponse(DrawBase):
    """Schema for Draw response"""
    id: int
    creator_id: Optional[int] = None
    share_link: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    participants: List[ParticipantResponse] = []

    class Config:
        from_attributes = True
