"""
LangChain tracing configuration for LangSmith.
"""
import os
import logging
from src.config.settings import get_settings

logger = logging.getLogger(__name__)

def setup_langchain_tracing():
    """
    Set up LangChain tracing with LangSmith.
    This enables monitoring, debugging, and evaluation of LangChain applications.
    """
    settings = get_settings()
    
    # Only set up tracing if API key is provided
    if not settings.LANGCHAIN_API_KEY:
        logger.warning("LangChain API key not provided. Tracing will not be enabled.")
        return
    
    # Set environment variables for LangChain tracing
    os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_TRACING_V2"] = str(settings.LANGCHAIN_TRACING_V2).lower()
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
    os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGCHAIN_ENDPOINT
    
    logger.info(f"LangChain tracing enabled for project: {settings.LANGCHAIN_PROJECT}")
    
    try:
        # Just import the core tracing module to verify it's available
        from langchain_core.tracers import langchain as lc_tracers
        
        # Log success
        logger.info("LangChain tracing modules imported successfully")
    except ImportError as e:
        logger.error(f"Failed to import LangChain tracing modules: {str(e)}")
    except Exception as e:
        logger.error(f"Error setting up LangChain tracing: {str(e)}") 