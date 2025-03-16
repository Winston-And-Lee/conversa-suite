from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, InvalidOperation
import logging
import time
import asyncio
from typing import Optional

from src.config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class MongoDB:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None
    connection_initialized = False
    connection_error = None
    last_connection_attempt = 0
    _lock = asyncio.Lock()  # Add a lock for thread safety

    @classmethod
    async def connect_to_database(cls):
        """Create database connection."""
        # Use a lock to prevent multiple concurrent connection attempts
        async with cls._lock:
            # Prevent connection attempts happening too frequently
            current_time = time.time()
            if current_time - cls.last_connection_attempt < 1.0:  # Wait at least 1 second between attempts
                logger.debug("Skipping connection attempt - too soon after previous attempt")
                if cls.connection_error:
                    raise RuntimeError(f"Previous connection error: {cls.connection_error}")
                return cls.db
                
            cls.last_connection_attempt = current_time
            
            try:
                logger.info("Connecting to MongoDB...")
                # Check if we already have a working connection
                if cls.client and cls.connection_initialized:
                    try:
                        # Test the connection with a ping
                        await cls.client.admin.command("ping")
                        logger.debug("Existing MongoDB connection is still valid")
                        return cls.db
                    except Exception as e:
                        logger.warning(f"Existing MongoDB connection failed ping test: {str(e)}")
                        # Continue with reconnection
                
                # Close any previous connection if it exists
                if cls.client:
                    logger.debug("Closing existing MongoDB connection")
                    try:
                        cls.client.close()
                    except Exception as e:
                        logger.warning(f"Error closing MongoDB connection: {str(e)}")
                    
                connection_uri = settings.MONGO_URI
                db_name = settings.MONGO_DB
                
                # Check if MongoDB URI is properly configured
                if not connection_uri or connection_uri == "mongodb://localhost:27017":
                    logger.warning("MongoDB URI appears to be using default values. Check your .env configuration.")
                
                logger.info(f"Connecting to database '{db_name}' at MongoDB server")
                # Don't log the full URI as it may contain credentials
                masked_uri = connection_uri.replace("://", "://***:***@") if "@" in connection_uri else connection_uri
                logger.debug(f"Using connection string: {masked_uri}")
                
                # Set a reasonable timeout for connection attempts
                cls.client = AsyncIOMotorClient(
                    connection_uri, 
                    serverSelectionTimeoutMS=5000,  # 5 second timeout
                    connectTimeoutMS=5000,
                    socketTimeoutMS=5000,
                    maxPoolSize=50,  # Increase connection pool size
                    minPoolSize=5,   # Maintain minimum connections
                    maxIdleTimeMS=60000,  # Keep connections alive for 60 seconds
                    retryWrites=True,  # Enable retry for write operations
                    retryReads=True    # Enable retry for read operations
                )
                cls.db = cls.client[db_name]
                
                # Verify connection with multiple checks
                logger.debug("Verifying MongoDB connection with ping...")
                await cls.client.admin.command("ping")
                
                # Try listing collections to verify DB access
                logger.debug(f"Verifying database '{db_name}' access...")
                collections = await cls.db.list_collection_names()
                logger.debug(f"Database contains {len(collections)} collections: {', '.join(collections) if collections else 'empty database'}")
                
                cls.connection_initialized = True
                cls.connection_error = None
                logger.info(f"Successfully connected to MongoDB database: {db_name}")
                return cls.db
            except Exception as e:
                cls.connection_initialized = False
                cls.connection_error = str(e)
                # Don't set client to None, as it might still be usable for future reconnection attempts
                logger.error(f"Failed to connect to MongoDB: {str(e)}")
                # Add more diagnostic information
                logger.error(f"Make sure MongoDB is running and accessible at the configured URI")
                logger.error(f"Current settings: MONGO_DB={settings.MONGO_DB}")
                raise RuntimeError(f"Failed to connect to MongoDB: {str(e)}")

    @classmethod
    async def reconnect_if_needed(cls) -> AsyncIOMotorDatabase:
        """Check connection and reconnect if needed."""
        try:
            if cls.client is None or cls.db is None or not cls.connection_initialized:
                logger.info("Database not connected, initializing connection...")
                return await cls.connect_to_database()
            else:
                try:
                    # Quick connection check
                    await cls.client.admin.command("ping")
                    logger.debug("Database connection verified with ping")
                    return cls.db
                except (ConnectionFailure, InvalidOperation) as e:
                    logger.warning(f"MongoDB connection lost: {str(e)}, attempting to reconnect...")
                    return await cls.connect_to_database()
                except Exception as e:
                    logger.error(f"Unexpected error checking MongoDB connection: {str(e)}")
                    return await cls.connect_to_database()
        except Exception as e:
            logger.error(f"Error in reconnect_if_needed: {str(e)}")
            raise

    @classmethod
    async def close_database_connection(cls):
        """Close database connection."""
        async with cls._lock:
            if cls.client:
                logger.info("Closing MongoDB connection...")
                try:
                    cls.client.close()
                    logger.info("MongoDB connection closed")
                except Exception as e:
                    logger.error(f"Error closing MongoDB connection: {str(e)}")
                finally:
                    # Even if there's an error, mark the connection as closed
                    cls.connection_initialized = False
                    # Don't set client to None, as it might still be usable for future reconnection attempts

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """Get database instance."""
        if cls.db is None or not cls.connection_initialized:
            error_msg = cls.connection_error if cls.connection_error else "Unknown error"
            logger.error(f"Database connection not established: {error_msg}")
            raise RuntimeError(f"Database connection not established. Call connect_to_database() first. Error: {error_msg}")
        return cls.db 