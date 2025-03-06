from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserVerification(BaseModel):
    """User verification domain entity."""
    id: Optional[str] = Field(None, alias="_id")
    email: EmailStr
    verification_code: str
    verification_token: Optional[str] = None
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_verified: bool = False
    verified_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        } 