from typing import Optional, List, Dict, Any
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from src.domain.models.user_verification import UserVerification
from src.domain.repository.user_verification_repository import UserVerificationRepository
import logging

logger = logging.getLogger(__name__)

class MongoDBUserVerificationRepository(UserVerificationRepository):
    """MongoDB implementation of UserVerificationRepository."""

    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize repository with database connection."""
        self.db = db
        self.collection = db["user_verifications"]
    
    async def create(self, verification: UserVerification) -> UserVerification:
        """Create a new verification record."""
        if self.db is None or self.collection is None:
            raise RuntimeError("Database connection not established")
            
        verification_dict = verification.dict(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(verification_dict)
        verification.id = str(result.inserted_id)
        return verification
    
    async def get_by_email(self, email: str) -> Optional[UserVerification]:
        """Get verification record by email."""
        if self.db is None or self.collection is None:
            raise RuntimeError("Database connection not established")
            
        result = await self.collection.find_one({"email": email})
        if result:
            result["_id"] = str(result["_id"])
            return UserVerification(**result)
        return None
    
    async def get_by_code(self, code: str) -> Optional[UserVerification]:
        """Get verification record by verification code."""
        if self.db is None or self.collection is None:
            raise RuntimeError("Database connection not established")
            
        result = await self.collection.find_one({"verification_code": code})
        if result:
            result["_id"] = str(result["_id"])
            return UserVerification(**result)
        return None
    
    async def update(self, verification_id: str, data: dict) -> Optional[UserVerification]:
        """Update a verification record."""
        if self.db is None or self.collection is None:
            raise RuntimeError("Database connection not established")
            
        # Add updated_at timestamp
        data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(verification_id)},
            {"$set": data}
        )
        
        if result.modified_count:
            updated = await self.collection.find_one({"_id": ObjectId(verification_id)})
            if updated:
                updated["_id"] = str(updated["_id"])
                return UserVerification(**updated)
        return None
    
    async def delete(self, verification_id: str) -> bool:
        """Delete a verification record."""
        if self.db is None or self.collection is None:
            raise RuntimeError("Database connection not established")
            
        result = await self.collection.delete_one({"_id": ObjectId(verification_id)})
        return result.deleted_count > 0
    
    async def mark_as_verified(self, verification_id: str) -> bool:
        """Mark a verification record as verified."""
        if self.db is None or self.collection is None:
            raise RuntimeError("Database connection not established")
            
        now = datetime.utcnow()
        result = await self.collection.update_one(
            {"_id": ObjectId(verification_id)},
            {"$set": {
                "is_verified": True,
                "verified_at": now,
                "updated_at": now
            }}
        )
        return result.modified_count > 0
    
    async def delete_expired(self, before_date: datetime) -> int:
        """Delete expired verification records."""
        if self.db is None or self.collection is None:
            raise RuntimeError("Database connection not established")
            
        result = await self.collection.delete_many({"expires_at": {"$lt": before_date}})
        return result.deleted_count 