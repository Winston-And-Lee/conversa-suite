from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime
import bcrypt
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from src.domain.models.user import User
from src.domain.repository.user_repository import UserRepository
from src.infrastructure.database.mongodb import MongoDB

logger = logging.getLogger(__name__)


class MongoDBUserRepository(UserRepository):
    """MongoDB implementation of UserRepository."""

    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        if db is not None:
            self.db = db
        else:
            try:
                self.db = MongoDB.get_db()
            except RuntimeError as e:
                print(f"Warning: {str(e)}")
                print("Proceeding with None database - repository operations will fail until connection is established")
                self.db = None
                return
        self.collection = self.db.users if self.db is not None else None

    async def create(self, user: User) -> User:
        """Create a new user."""
        if self.db is None or self.collection is None:
            raise RuntimeError("Database connection not established")
            
        # Hash the password before storing
        if user.password_hash and not user.password_hash.startswith('$2b$'):
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(user.password_hash.encode('utf-8'), salt)
            user.password_hash = hashed_password.decode('utf-8')
        
        # Set timestamps if not set
        if not user.created_at:
            user.created_at = datetime.utcnow()
        if not user.updated_at:
            user.updated_at = user.created_at
            
        user_dict = user.model_dump(exclude={"id"})
        result = await self.collection.insert_one(user_dict)
        user.id = str(result.inserted_id)
        return user

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        if self.db is None or self.collection is None:
            raise RuntimeError("Database connection not established")
            
        user_dict = await self.collection.find_one({"_id": ObjectId(user_id)})
        if user_dict:
            user_dict["id"] = str(user_dict.pop("_id"))
            return User(**user_dict)
        return None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        if self.db is None or self.collection is None:
            raise RuntimeError("Database connection not established")
            
        user_dict = await self.collection.find_one({"email": email})
        if user_dict:
            user_dict["id"] = str(user_dict.pop("_id"))
            return User(**user_dict)
        return None

    async def get_all(self) -> List[User]:
        """Get all users."""
        if self.db is None or self.collection is None:
            raise RuntimeError("Database connection not established")
            
        users = []
        cursor = self.collection.find()
        async for user_dict in cursor:
            user_dict["id"] = str(user_dict.pop("_id"))
            users.append(User(**user_dict))
        return users

    async def update(self, user_id: str, user_data: dict) -> Optional[User]:
        """Update user."""
        if self.db is None or self.collection is None:
            raise RuntimeError("Database connection not established")
            
        # Add updated timestamp
        user_data['updated_at'] = datetime.utcnow()
        
        # Handle password hashing if present
        if 'password_hash' in user_data and user_data['password_hash'] and not user_data['password_hash'].startswith('$2b$'):
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(user_data['password_hash'].encode('utf-8'), salt)
            user_data['password_hash'] = hashed_password.decode('utf-8')
            
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": user_data}
        )
        if result.modified_count == 1:
            return await self.get_by_id(user_id)
        return None

    async def delete(self, user_id: str) -> bool:
        """Delete user."""
        if self.db is None or self.collection is None:
            raise RuntimeError("Database connection not established")
            
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count == 1
        
    async def verify_password(self, email: str, password: str) -> Optional[User]:
        """Verify user password and return user if valid."""
        if self.db is None or self.collection is None:
            raise RuntimeError("Database connection not established")
            
        # Get user by email
        user = await self.get_by_email(email)
        if not user:
            return None
        
        # Verify password hash
        if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return user
        return None

    async def store_refresh_token(self, user_id: str, token: str) -> bool:
        """Store refresh token for a user."""
        if self.db is None or self.collection is None:
            raise RuntimeError("Database connection not established")
            
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {"refresh_tokens": token}}
        )
        return result.modified_count == 1
        
    async def invalidate_refresh_token(self, token: str) -> bool:
        """Remove a refresh token (logout)."""
        try:
            result = await self.db.users.update_one(
                {"refresh_tokens": token},
                {"$pull": {"refresh_tokens": token}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error invalidating refresh token: {str(e)}")
            return False

    async def get_user_id_by_refresh_token(self, token: str) -> Optional[str]:
        """Get user ID associated with a refresh token."""
        if self.db is None or self.collection is None:
            raise RuntimeError("Database connection not established")
            
        # Find user with the specified refresh token
        user = await self.collection.find_one({"refresh_tokens": token})
        if not user:
            return None
            
        # Return the user ID as a string
        return str(user["_id"]) 