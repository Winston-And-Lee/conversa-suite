from typing import Optional
from pydantic import BaseModel
from src.domain.models.user import User


class AuthResponse(BaseModel):
    """Base authentication response."""
    user: Optional[User] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None

    @classmethod
    def create(cls, user: Optional[User], access_token: Optional[str], refresh_token: Optional[str]) -> 'AuthResponse':
        """Factory method to create an AuthResponse."""
        return cls(
            user=user,
            access_token=access_token,
            refresh_token=refresh_token
        )

    @classmethod
    def error(cls) -> 'AuthResponse':
        """Factory method to create an error AuthResponse."""
        return cls(
            user=None,
            access_token=None,
            refresh_token=None
        )


class RefreshTokenResponse(BaseModel):
    """Refresh token response."""
    user: Optional[User] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    
    @classmethod
    def create(cls, user: Optional[User], access_token: Optional[str], refresh_token: Optional[str]) -> 'RefreshTokenResponse':
        """Factory method to create a RefreshTokenResponse."""
        return cls(
            user=user,
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    @classmethod
    def error(cls) -> 'RefreshTokenResponse':
        """Factory method to create an error RefreshTokenResponse."""
        return cls(
            user=None,
            access_token=None,
            refresh_token=None
        ) 