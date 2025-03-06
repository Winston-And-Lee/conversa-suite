from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    """Base model for user data."""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    """Model for creating a new user."""
    password: str
    
    @validator('password')
    def password_complexity(cls, v):
        """Validate password complexity."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(BaseModel):
    """Model for updating user data."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Model for user response data."""
    _id: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime


class UserLogin(BaseModel):
    """Model for user login data."""
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    """Model for user login response data."""
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str


class UserRefreshToken(BaseModel):
    """Model for refreshing an access token."""
    refresh_token: str


class UserRefreshResponse(BaseModel):
    """Model for token refresh response."""
    access_token: str
    refresh_token: str
    token_type: str


class UserResetPassword(BaseModel):
    """Model for resetting a user's password."""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def password_complexity(cls, v):
        """Validate password complexity."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserVerification(BaseModel):
    """Model for requesting user verification."""
    email: EmailStr


class UserVerify(BaseModel):
    """Model for verifying a user."""
    email: Optional[EmailStr] = None
    code: str
    reference_token: Optional[str] = None


class UserProfile(BaseModel):
    """Model for user profile data."""
    _id: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    is_admin: bool 