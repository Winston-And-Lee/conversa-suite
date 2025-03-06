from src.usecase.user.user_usecase import UserUsecase
from src.interface.repository.database.db_repository import user_repository, ensure_db_connected

# Create and export a singleton instance
_user_usecase = None

async def get_user_usecase_async():
    """Get the singleton instance of the user usecase with async initialization."""
    global _user_usecase
    if _user_usecase is None:
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Initializing user usecase")
        
        _user_usecase = UserUsecase()
        # Ensure database is connected before creating repositories
        try:
            # We'll try to connect with retries
            from src.interface.repository.database.db_repository import ensure_db_connected
            from src.interface.repository.database.db_repository import user_repository, user_verification_repository
            db = await ensure_db_connected(max_retries=3, retry_delay=1.0)
            
            # Create the repositories with the connected database
            _user_usecase.user_repository = user_repository()
            _user_usecase.user_verification_repository = user_verification_repository()
            
            logger.info("User usecase initialized successfully with database connections")
        except Exception as e:
            logger.error(f"Failed to connect to database in get_user_usecase_async: {str(e)}")
            _user_usecase.user_repository = None
            _user_usecase.user_verification_repository = None
    elif _user_usecase.user_repository is None or _user_usecase.user_verification_repository is None:
        # If usecase exists but repositories are None, try to reconnect
        import logging
        logger = logging.getLogger(__name__)
        logger.warning("User usecase exists but repositories are None, attempting to reconnect")
        
        try:
            from src.interface.repository.database.db_repository import ensure_db_connected
            from src.interface.repository.database.db_repository import user_repository, user_verification_repository
            await ensure_db_connected(max_retries=2, retry_delay=0.5)
            
            if _user_usecase.user_repository is None:
                _user_usecase.user_repository = user_repository()
                
            if _user_usecase.user_verification_repository is None:
                _user_usecase.user_verification_repository = user_verification_repository()
                
            logger.info("Successfully reconnected and initialized user repositories")
        except Exception as e:
            logger.error(f"Failed to reconnect to database in get_user_usecase_async: {str(e)}")
    
    return _user_usecase

def get_user_usecase():
    """
    Get the singleton instance of the user usecase.
    Note: This synchronous version should only be used after the database 
    is confirmed to be connected (e.g., after application startup).
    """
    global _user_usecase
    if _user_usecase is None:
        _user_usecase = UserUsecase()
        # Inject the repository
        try:
            _user_usecase.user_repository = user_repository()
        except RuntimeError as e:
            print(f"Warning: Failed to initialize user repository: {str(e)}")
            _user_usecase.user_repository = None
    return _user_usecase

# For backwards compatibility in existing code
__all__ = ["UserUsecase", "get_user_usecase", "get_user_usecase_async"] 