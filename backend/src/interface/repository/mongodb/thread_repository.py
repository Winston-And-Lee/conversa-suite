"""
MongoDB implementation of the ThreadRepository.
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.domain.repository.thread_repository import ThreadRepository
from src.domain.models.thread import ThreadModel
from src.infrastructure.database.mongodb import MongoDB

logger = logging.getLogger(__name__)

class MongoDBThreadRepository(ThreadRepository):
    """MongoDB implementation of the ThreadRepository."""
    
    COLLECTION_NAME = "threads"
    
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        if db is not None:
            self.db = db
    
    async def create_thread(self, thread_data: Dict[str, Any]) -> str:
        """
        Create a new thread in MongoDB.
        
        Args:
            thread_data: The thread data to create
            
        Returns:
            The ID of the created thread
        """
        try:
            db = await MongoDB.reconnect_if_needed()
            collection = db[self.COLLECTION_NAME]
            
            # Add timestamps
            thread_data["created_at"] = datetime.utcnow()
            thread_data["updated_at"] = datetime.utcnow()
            
            # Insert the thread
            result = await collection.insert_one(thread_data)
            
            logger.info(f"Created thread with ID: {thread_data['thread_id']}")
            return thread_data["thread_id"]
        except Exception as e:
            logger.error(f"Error creating thread: {str(e)}")
            raise
    
    async def get_thread(self, thread_id: str) -> Optional[ThreadModel]:
        """
        Get a thread by ID from MongoDB.
        
        Args:
            thread_id: The ID of the thread to get
            
        Returns:
            The thread or None if not found
        """
        try:
            db = await MongoDB.reconnect_if_needed()
            collection = db[self.COLLECTION_NAME]
            
            # Find the thread
            thread_data = await collection.find_one({"thread_id": thread_id})
            
            if thread_data:
                # Convert ObjectId to string for serialization
                if "_id" in thread_data:
                    thread_data["_id"] = str(thread_data["_id"])
                
                return ThreadModel(**thread_data)
            
            return None
        except Exception as e:
            logger.error(f"Error getting thread {thread_id}: {str(e)}")
            raise
    
    async def update_thread(self, thread_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update a thread in MongoDB.
        
        Args:
            thread_id: The ID of the thread to update
            update_data: The data to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            db = await MongoDB.reconnect_if_needed()
            collection = db[self.COLLECTION_NAME]
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            # Update the thread
            result = await collection.update_one(
                {"thread_id": thread_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating thread {thread_id}: {str(e)}")
            raise
    
    async def delete_thread(self, thread_id: str) -> bool:
        """
        Delete a thread from MongoDB.
        
        Args:
            thread_id: The ID of the thread to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            db = await MongoDB.reconnect_if_needed()
            collection = db[self.COLLECTION_NAME]
            
            # Delete the thread
            result = await collection.delete_one({"thread_id": thread_id})
            
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting thread {thread_id}: {str(e)}")
            raise
    
    async def list_threads_by_user(self, user_id: str, limit: int = 20, skip: int = 0) -> List[ThreadModel]:
        """
        List threads by user ID from MongoDB.
        
        Args:
            user_id: The ID of the user
            limit: The maximum number of threads to return
            skip: The number of threads to skip
            
        Returns:
            A list of threads
        """
        try:
            db = await MongoDB.reconnect_if_needed()
            collection = db[self.COLLECTION_NAME]
            
            # Find threads by user ID
            cursor = collection.find(
                {"user_id": user_id, "is_archived": False}
            ).sort("updated_at", -1).skip(skip).limit(limit)
            
            threads = []
            async for thread_data in cursor:
                # Convert ObjectId to string for serialization
                if "_id" in thread_data:
                    thread_data["_id"] = str(thread_data["_id"])
                
                threads.append(ThreadModel(**thread_data))
            
            return threads
        except Exception as e:
            logger.error(f"Error listing threads for user {user_id}: {str(e)}")
            raise
    
    async def add_message_to_thread(self, thread_id: str, message: Dict[str, Any]) -> bool:
        """
        Add a message to a thread in MongoDB.
        
        Args:
            thread_id: The ID of the thread
            message: The message to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            db = await MongoDB.reconnect_if_needed()
            collection = db[self.COLLECTION_NAME]
            
            # Update the thread with the new message
            result = await collection.update_one(
                {"thread_id": thread_id},
                {
                    "$push": {"messages": message},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error adding message to thread {thread_id}: {str(e)}")
            raise
    
    async def update_thread_summary(self, thread_id: str, summary: str) -> bool:
        """
        Update the summary of a thread in MongoDB.
        
        Args:
            thread_id: The ID of the thread
            summary: The new summary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            db = await MongoDB.reconnect_if_needed()
            collection = db[self.COLLECTION_NAME]
            
            # Update the thread summary
            result = await collection.update_one(
                {"thread_id": thread_id},
                {
                    "$set": {
                        "summary": summary,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating summary for thread {thread_id}: {str(e)}")
            raise 