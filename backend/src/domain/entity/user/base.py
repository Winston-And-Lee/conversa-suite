from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """User registration data."""
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None 