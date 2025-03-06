from src.domain.repository.user_repository import UserRepository
from src.domain.repository.user_verification_repository import UserVerificationRepository
from src.infrastructure.database.mongodb import MongoDB
from src.interface.repository.mongodb.user_repository import MongoDBUserRepository
from src.interface.repository.mongodb.user_verification_repository import MongoDBUserVerificationRepository
import logging
import asyncio

logger = logging.getLogger(__name__)

async def ensure_db_connected(max_retries=3, retry_delay=1.0):
    """
    Ensures that the database connection is established.
    This should be called before creating any repositories.
    
    Args:
        max_retries: Maximum number of connection attempts
        retry_delay: Delay between retries in seconds
        
    Returns:
        Database instance if connection is successful
        
    Raises:
        RuntimeError: If connection cannot be established after max_retries
    """
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # Use the reconnect method to ensure we have a valid connection
            logger.info(f"Database connection attempt {attempt + 1}/{max_retries}")
            db = await MongoDB.reconnect_if_needed()
            logger.info("Database connection established successfully")
            return db
        except Exception as e:
            last_error = str(e)
            logger.warning(f"Failed to connect to database (attempt {attempt + 1}/{max_retries}): {last_error}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
    
    # If we get here, all retries failed
    error_message = f"Failed to connect to database after {max_retries} attempts. Last error: {last_error}"
    logger.error(error_message)
    raise RuntimeError(error_message)


def user_repository() -> UserRepository:
    """
    Factory function that returns a UserRepository implementation.
    This centralizes the creation of repository instances.
    
    Note: Make sure the database is connected by calling ensure_db_connected()
    before using this function.
    """
    try:
        db = MongoDB.get_db()
        return MongoDBUserRepository(db)
    except RuntimeError as e:
        logger.error(f"Failed to create user repository: {str(e)}")
        raise

def user_verification_repository() -> UserVerificationRepository:
    """
    Factory function that returns a UserVerificationRepository implementation.
    This centralizes the creation of repository instances.
    
    Note: Make sure the database is connected by calling ensure_db_connected()
    before using this function.
    """
    try:
        db = MongoDB.get_db()
        return MongoDBUserVerificationRepository(db)
    except RuntimeError as e:
        logger.error(f"Failed to create user verification repository: {str(e)}")
        raise


# Add more repository factory functions as needed, for example:
# def workspace_repository() -> WorkspaceRepository:
#     db = MongoDB.get_db()
#     return MongoDBWorkspaceRepository(db) 