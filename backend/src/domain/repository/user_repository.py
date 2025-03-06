from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models.user import User


class UserRepository(ABC):
    """Abstract base class for user repository."""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user."""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass

    @abstractmethod
    async def get_all(self) -> List[User]:
        """Get all users."""
        pass

    @abstractmethod
    async def update(self, user_id: str, user_data: dict) -> Optional[User]:
        """Update user."""
        pass

    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Delete user."""
        pass
        
    @abstractmethod
    async def verify_password(self, email: str, password: str) -> Optional[User]:
        """Verify user password and return user if valid."""
        pass
        
    @abstractmethod
    async def store_refresh_token(self, user_id: str, token: str) -> bool:
        """Store refresh token for a user."""
        pass
        
    @abstractmethod
    async def invalidate_refresh_token(self, token: str) -> bool:
        """Remove a refresh token (logout)."""
        pass
        
    @abstractmethod
    async def get_user_id_by_refresh_token(self, token: str) -> Optional[str]:
        """Get user ID associated with a refresh token."""
        pass 