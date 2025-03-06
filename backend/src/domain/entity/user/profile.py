from typing import Optional
from pydantic import BaseModel
from src.domain.models.user import User


class ProfileResponse(BaseModel):
    """Response for user profile operations."""
    user: Optional[User] = None
    success: bool = False
    
    @classmethod
    def create(cls, user: User) -> 'ProfileResponse':
        """Factory method to create a successful profile response."""
        return cls(
            user=user,
            success=True
        )
    
    @classmethod
    def error(cls) -> 'ProfileResponse':
        """Factory method to create an error profile response."""
        return cls(
            user=None,
            success=False
        )


class PasswordResetResponse(BaseModel):
    """Response for password reset operations."""
    success: bool = False
    message: str = ""
    
    @classmethod
    def create(cls, message: str = "Password reset successfully") -> 'PasswordResetResponse':
        """Factory method to create a successful password reset response."""
        return cls(
            success=True,
            message=message
        )
    
    @classmethod
    def error(cls, message: str = "Failed to reset password") -> 'PasswordResetResponse':
        """Factory method to create an error password reset response."""
        return cls(
            success=False,
            message=message
        ) 