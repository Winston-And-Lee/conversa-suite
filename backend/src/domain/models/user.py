from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    """User domain entity."""
    id: Optional[str] = Field(None, alias="_id")
    email: EmailStr
    password_hash: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_verified: bool = False  # Keep this field for quick verification checks
    
    # OAuth fields
    google_id: Optional[str] = None
    microsoft_id: Optional[str] = None
    
    # Token management
    refresh_tokens: List[str] = []

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        } 