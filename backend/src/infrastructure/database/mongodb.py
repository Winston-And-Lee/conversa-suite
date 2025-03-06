from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
import logging
import time

from src.config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class MongoDB:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None
    connection_initialized = False
    connection_error = None
    last_connection_attempt = 0

    @classmethod
    async def connect_to_database(cls):
        """Create database connection."""
        # Prevent connection attempts happening too frequently
        current_time = time.time()
        if current_time - cls.last_connection_attempt < 1.0:  # Wait at least 1 second between attempts
            logger.debug("Skipping connection attempt - too soon after previous attempt")
            if cls.connection_error:
                raise RuntimeError(f"Previous connection error: {cls.connection_error}")
            return
            
        cls.last_connection_attempt = current_time
        
        try:
            logger.info("Connecting to MongoDB...")
            # Clear any previous connection if it exists
            if cls.client:
                logger.debug("Closing existing MongoDB connection")
                cls.client.close()
                
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
                socketTimeoutMS=5000
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
            cls.client = None
            cls.db = None
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            # Add more diagnostic information
            logger.error(f"Make sure MongoDB is running and accessible at the configured URI")
            logger.error(f"Current settings: MONGO_DB={settings.MONGO_DB}")
            raise RuntimeError(f"Failed to connect to MongoDB: {str(e)}")

    @classmethod
    async def reconnect_if_needed(cls):
        """Check connection and reconnect if needed."""
        if cls.client is None or cls.db is None or not cls.connection_initialized:
            logger.info("Database not connected, initializing connection...")
            await cls.connect_to_database()
        else:
            try:
                # Quick connection check
                await cls.client.admin.command("ping")
                logger.debug("Database connection verified with ping")
            except Exception as e:
                logger.warning(f"MongoDB connection lost: {str(e)}, attempting to reconnect...")
                await cls.connect_to_database()
        return cls.db

    @classmethod
    async def close_database_connection(cls):
        """Close database connection."""
        if cls.client:
            logger.info("Closing MongoDB connection...")
            cls.client.close()
            cls.connection_initialized = False
            cls.db = None
            cls.client = None
            logger.info("MongoDB connection closed")

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """Get database instance."""
        if cls.db is None or not cls.connection_initialized:
            error_msg = cls.connection_error if cls.connection_error else "Unknown error"
            logger.error(f"Database connection not established: {error_msg}")
            raise RuntimeError(f"Database connection not established. Call connect_to_database() first. Error: {error_msg}")
        return cls.db 