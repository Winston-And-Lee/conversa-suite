#!/usr/bin/env python3
"""
Script to test the Pinecone connection.
This script initializes the Pinecone client and tests basic operations.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to the path so we can import from the backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env.test file
env_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / ".env.test"
load_dotenv(dotenv_path=env_path)

from src.interface.repository.pinecone.pinecone_repository import PineconeRepository
from src.config.settings import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_pinecone_connection():
    """Test the Pinecone connection."""
    try:
        # Get settings
        settings = get_settings()
        logger.info(f"Testing Pinecone connection with index: {settings.PINECONE_INDEX_NAME}")
        
        # Initialize Pinecone repository
        pinecone_repo = PineconeRepository()
        logger.info("Pinecone repository initialized successfully")
        
        # Test generating embeddings
        test_text = "This is a test text for generating embeddings."
        embeddings = await pinecone_repo.generate_embeddings(test_text)
        logger.info(f"Generated embeddings with {len(embeddings)} dimensions")
        
        # Test upserting a vector
        test_data = {
            "title": "Test Title",
            "specified_text": "Test specified text",
            "content": "Test content",
            "file_text": "",
            "keywords": ["test", "pinecone", "connection"]
        }
        test_metadata = {
            "mongodb_id": "test_id",
            "title": "Test Title",
            "specified_text": "Test specified text",
            "data_type": "TEST",
            "content": "Test content",
            "reference": "Test reference",
            "file_url": "https://example.com/test-file.pdf",
            "has_file": True,
            "user_id": "test_user_id"
        }
        
        vector_id = await pinecone_repo.upsert_vector(test_data, test_metadata)
        logger.info(f"Upserted vector with ID: {vector_id}")
        
        # Test searching
        search_results = await pinecone_repo.search("test", limit=5)
        logger.info(f"Search returned {len(search_results)} results")
        
        # Test loading a file from URL (optional, only if a valid PDF URL is available)
        test_pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
        try:
            logger.info(f"Testing file loading from URL: {test_pdf_url}")
            file_vector_ids = await pinecone_repo.load_file_from_url(test_pdf_url, test_metadata)
            logger.info(f"Successfully loaded file from URL, created {len(file_vector_ids)} vectors")
            
            # Clean up the file vectors
            for vid in file_vector_ids:
                await pinecone_repo.delete_vector(vid)
            logger.info(f"Cleaned up {len(file_vector_ids)} file vectors")
        except Exception as e:
            logger.warning(f"File loading test skipped or failed: {str(e)}")
        
        # Test deleting the vector
        deleted = await pinecone_repo.delete_vector(vector_id)
        logger.info(f"Vector deletion {'successful' if deleted else 'failed'}")
        
        logger.info("All Pinecone tests completed successfully")
        
    except Exception as e:
        logger.error(f"Error testing Pinecone connection: {str(e)}")
        raise

async def main():
    """Main function."""
    logger.info("Starting Pinecone connection test...")
    await test_pinecone_connection()
    logger.info("Pinecone connection test completed")

if __name__ == "__main__":
    asyncio.run(main()) 