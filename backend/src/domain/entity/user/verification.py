from typing import Optional
from pydantic import BaseModel
from src.domain.models.user import User


class VerificationRequestResponse(BaseModel):
    """Response for verification request."""
    reference_token: Optional[str] = None
    success: bool = False
    
    @classmethod
    def create(cls, reference_token: str) -> 'VerificationRequestResponse':
        """Factory method to create a successful verification request response."""
        return cls(
            reference_token=reference_token,
            success=True
        )
    
    @classmethod
    def error(cls) -> 'VerificationRequestResponse':
        """Factory method to create an error verification request response."""
        return cls(
            reference_token=None,
            success=False
        )


class VerificationResponse(BaseModel):
    """Response for user verification."""
    user: Optional[User] = None
    success: bool = False
    
    @classmethod
    def create(cls, user: User) -> 'VerificationResponse':
        """Factory method to create a successful verification response."""
        return cls(
            user=user,
            success=True
        )
    
    @classmethod
    def error(cls) -> 'VerificationResponse':
        """Factory method to create an error verification response."""
        return cls(
            user=None,
            success=False
        ) 