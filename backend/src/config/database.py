import os
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

# Global database client instance
_db_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


async def get_database() -> AsyncIOMotorDatabase:
    """
    Get the database instance.
    
    Returns:
        AsyncIOMotorDatabase: MongoDB database instance
    """
    global _db_client, _db
    
    if _db is None:
        await connect_to_mongo()
    
    return _db


async def connect_to_mongo():
    """Connect to MongoDB and set up the database client."""
    global _db_client, _db
    
    try:
        # Get MongoDB configuration from environment variables
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        mongo_db = os.getenv("MONGO_DB", "backend_db")
        mongo_user = os.getenv("MONGO_USER")
        mongo_password = os.getenv("MONGO_PASSWORD")
        
        # Add authentication if username and password are provided
        if mongo_user and mongo_password:
            mongo_uri = mongo_uri.replace("mongodb://", f"mongodb://{mongo_user}:{mongo_password}@")
        
        # Create client and connect
        _db_client = AsyncIOMotorClient(mongo_uri)
        _db = _db_client[mongo_db]
        
        # Test connection
        await _db_client.admin.command('ping')
        logger.info(f"Connected to MongoDB at {mongo_uri}")
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise


async def close_mongo_connection():
    """Close the MongoDB connection."""
    global _db_client
    
    if _db_client:
        _db_client.close()
        logger.info("Closed MongoDB connection") 