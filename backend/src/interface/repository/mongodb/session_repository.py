"""
Repository for storing assistant sessions in MongoDB.
"""
import logging
from typing import Dict, Any, Optional
import json
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.infrastructure.database.mongodb import MongoDB

logger = logging.getLogger(__name__)

class MongoDBSessionRepository:
    """Repository for storing assistant sessions in MongoDB."""
    
    COLLECTION_NAME = "assistant_sessions"
    
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        """Initialize the repository."""
        if db is not None:
            self.db = db
            self.collection = self.db.assistant_sessions
        else:
            self.db = None
            self.collection = None
    
    async def save_session(self, thread_id: str, state: Dict[str, Any]) -> bool:
        """
        Save an assistant session state to MongoDB.
        
        Args:
            thread_id: The ID of the thread
            state: The state to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            await self._ensure_db_connection()
                
            # Convert state to a serializable format
            serialized_state = self._serialize_state(state)
            
            # Upsert the state
            result = await self.collection.update_one(
                {"thread_id": thread_id},
                {"$set": {"state": serialized_state}},
                upsert=True
            )
            
            return result.acknowledged
        except Exception as e:
            logger.error(f"Error saving session {thread_id}: {str(e)}")
            return False
    
    async def get_session(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an assistant session state from MongoDB.
        
        Args:
            thread_id: The ID of the thread
            
        Returns:
            The state if found, None otherwise
        """
        try:
            await self._ensure_db_connection()
                
            # Get the state
            result = await self.collection.find_one({"thread_id": thread_id})
            
            if not result:
                return None
            
            # Deserialize the state
            return self._deserialize_state(result["state"])
        except Exception as e:
            logger.error(f"Error getting session {thread_id}: {str(e)}")
            return None
    
    async def delete_session(self, thread_id: str) -> bool:
        """
        Delete an assistant session state from MongoDB.
        
        Args:
            thread_id: The ID of the thread
            
        Returns:
            True if successful, False otherwise
        """
        try:
            await self._ensure_db_connection()
                
            # Delete the state
            result = await self.collection.delete_one({"thread_id": thread_id})
            
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting session {thread_id}: {str(e)}")
            return False
    
    async def _ensure_db_connection(self):
        """Ensure database connection is established."""
        try:
            # If we already have a connection, use it
            if self.db is not None and self.collection is not None:
                return
                
            # Otherwise, get a new connection
            self.db = await MongoDB.reconnect_if_needed()
            self.collection = self.db.assistant_sessions
            
            if self.db is None or self.collection is None:
                raise RuntimeError("Failed to establish database connection")
                
        except Exception as e:
            logger.error(f"Failed to establish database connection: {str(e)}")
            raise RuntimeError(f"Database connection not established: {str(e)}")
    
    def _serialize_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Serialize a state for storage in MongoDB.
        
        Args:
            state: The state to serialize
            
        Returns:
            The serialized state
        """
        # Create a deep copy to avoid modifying the original
        serialized = {}
        
        # Handle special objects that need serialization
        for key, value in state.items():
            if isinstance(value, dict):
                serialized[key] = self._serialize_state(value)
            elif isinstance(value, list):
                serialized[key] = [
                    self._serialize_state(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                # Convert any non-serializable objects to strings
                try:
                    # Test if it's JSON serializable
                    json.dumps(value)
                    serialized[key] = value
                except (TypeError, OverflowError):
                    # If not serializable, convert to string
                    serialized[key] = str(value)
        
        return serialized
    
    def _deserialize_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deserialize a state from MongoDB.
        
        Args:
            state: The state to deserialize
            
        Returns:
            The deserialized state
        """
        # Create a deep copy to avoid modifying the original
        deserialized = {}
        
        # Handle special objects that need deserialization
        for key, value in state.items():
            if isinstance(value, dict):
                deserialized[key] = self._deserialize_state(value)
            elif isinstance(value, list):
                deserialized[key] = [
                    self._deserialize_state(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                deserialized[key] = value
        
        return deserialized 