from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime

from src.domain.models.user_verification import UserVerification


class UserVerificationRepository(ABC):
    """Interface for user verification repository."""
    
    @abstractmethod
    async def create(self, verification: UserVerification) -> UserVerification:
        """Create a new verification record."""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserVerification]:
        """Get verification record by email."""
        pass
    
    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[UserVerification]:
        """Get verification record by verification code."""
        pass
    
    @abstractmethod
    async def update(self, verification_id: str, data: dict) -> Optional[UserVerification]:
        """Update a verification record."""
        pass
    
    @abstractmethod
    async def delete(self, verification_id: str) -> bool:
        """Delete a verification record."""
        pass
    
    @abstractmethod
    async def mark_as_verified(self, verification_id: str) -> bool:
        """Mark a verification record as verified."""
        pass
    
    @abstractmethod
    async def delete_expired(self, before_date: datetime) -> int:
        """Delete expired verification records."""
        pass 