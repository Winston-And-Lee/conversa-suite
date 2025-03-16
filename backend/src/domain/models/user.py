from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class User(BaseModel):
    """User domain entity."""
    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={
            datetime: lambda dt: dt.isoformat()
        }
    )
    
    id: Optional[str] = None
    email: str
    username: Optional[str] = None
    password_hash: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    is_admin: bool = False
    refresh_tokens: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    profile_picture: Optional[str] = None
    auth_provider: Optional[str] = None  # "google", "microsoft", etc.
    auth_provider_id: Optional[str] = None  # ID from the auth provider
    
    # OAuth fields
    google_id: Optional[str] = None
    microsoft_id: Optional[str] = None 