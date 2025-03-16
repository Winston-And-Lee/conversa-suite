from src.domain.repository.user_repository import UserRepository
from src.domain.repository.user_verification_repository import UserVerificationRepository
from src.infrastructure.database.mongodb import MongoDB
from src.interface.repository.mongodb.user_repository import MongoDBUserRepository
from src.interface.repository.mongodb.user_verification_repository import MongoDBUserVerificationRepository
from src.interface.repository.mongodb.data_ingestion_repository import DataIngestionRepository
from src.interface.repository.mongodb.file_resource_repository import FileResourceRepository
from src.interface.repository.mongodb.thread_repository import MongoDBThreadRepository
from src.interface.repository.s3.s3_repository import S3Repository
from src.interface.repository.file.file_repository import S3FileRepository
from src.interface.repository.pinecone.pinecone_repository import PineconeRepository
import logging
import asyncio

logger = logging.getLogger(__name__)

async def ensure_db_connected(max_retries=3, retry_delay=1.0):
    """
    Ensures that the database is connected before proceeding.
    This function tries to connect to the database and retries
    in case of failure.

    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Raises:
        RuntimeError: If all retry attempts fail
    """
    last_error = None
    for attempt in range(max_retries):
        try:
            # Attempt to connect to MongoDB
            await MongoDB.connect_to_database()
            logger.info("Successfully connected to database")
            return
        except Exception as e:
            last_error = e
            logger.warning(f"Failed to connect to database (attempt {attempt + 1}/{max_retries}): {str(e)}")
            
            # Don't wait if this is the last attempt
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

def data_ingestion_repository() -> DataIngestionRepository:
    """
    Factory function that returns a DataIngestionRepository implementation.
    This centralizes the creation of repository instances.
    
    Note: Make sure the database is connected by calling ensure_db_connected()
    before using this function.
    """
    try:
        db = MongoDB.get_db()
        return DataIngestionRepository(db)
    except RuntimeError as e:
        logger.error(f"Failed to create data ingestion repository: {str(e)}")
        raise

def file_resource_repository() -> FileResourceRepository:
    """
    Factory function that returns a FileResourceRepository implementation.
    This centralizes the creation of repository instances.
    
    Note: Make sure the database is connected by calling ensure_db_connected()
    before using this function.
    """
    try:
        db = MongoDB.get_db()
        return FileResourceRepository(db)
    except RuntimeError as e:
        logger.error(f"Failed to create file resource repository: {str(e)}")
        raise

def s3_repository() -> S3Repository:
    """
    Factory function that returns an S3Repository implementation.
    This centralizes the creation of repository instances.
    """
    try:
        return S3Repository()
    except Exception as e:
        logger.error(f"Failed to create S3 repository: {str(e)}")
        raise

def file_repository():
    """
    Factory function that returns a FileRepository implementation.
    This centralizes the creation of repository instances.
    """
    try:
        return S3FileRepository()
    except Exception as e:
        logger.error(f"Failed to create file repository: {str(e)}")
        raise

def pinecone_repository() -> PineconeRepository:
    """
    Factory function that returns a PineconeRepository implementation.
    This centralizes the creation of repository instances.
    """
    try:
        return PineconeRepository()
    except Exception as e:
        logger.error(f"Failed to create Pinecone repository: {str(e)}")
        raise

def thread_repository():
    """
    Factory function that returns a MongoDBThreadRepository implementation.
    This centralizes the creation of repository instances.
    
    Note: Make sure the database is connected by calling ensure_db_connected()
    before using this function.
    """
    try:
        db = MongoDB.get_db()
        return MongoDBThreadRepository(db)
    except RuntimeError as e:
        logger.error(f"Failed to create thread repository: {str(e)}")
        raise

def get_repository(repository_name: str):
    """
    Get a repository by name.
    
    Args:
        repository_name: Name of the repository to get
        
    Returns:
        Repository instance
        
    Raises:
        ValueError: If repository name is not recognized
    """
    repositories = {
        "user": user_repository,
        "user_verification": user_verification_repository,
        "data_ingestion": data_ingestion_repository,
        "file_resource": file_resource_repository,
        "s3": s3_repository,
        "file": file_repository,
        "pinecone": pinecone_repository,
        "thread": thread_repository
    }
    
    if repository_name not in repositories:
        raise ValueError(f"Repository '{repository_name}' not found")
    
    return repositories[repository_name]()


# Add more repository factory functions as needed, for example:
# def workspace_repository() -> WorkspaceRepository:
#     db = MongoDB.get_db()
#     return MongoDBWorkspaceRepository(db) 