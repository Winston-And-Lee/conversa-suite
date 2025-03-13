#!/usr/bin/env python3
"""
Script to test the data ingestion process with a webpage URL.
This script tests the entire flow from submitting a webpage URL to storing it in MongoDB and Pinecone.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import List, Dict, Any
import uuid
from datetime import datetime

# Add the backend directory to the path so we can import modules
sys.path.append(str(Path(__file__).parent.parent))

# Import required modules
from src.domain.models.data_ingestion import DataIngestion, DataType
from src.domain.models.user import User
from src.usecase.data_ingestion.data_ingestion_usecase import DataIngestionUseCase
from src.interface.repository.database.db_repository import data_ingestion_repository, pinecone_repository
from src.config.settings import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
settings = get_settings()

async def test_data_ingestion_with_webpage():
    """Test data ingestion with a webpage URL."""
    try:
        logger.info("Starting data ingestion test with webpage URL...")
        
        # Create a mock user
        mock_user = User(
            id=str(uuid.uuid4()),
            username="test_user",
            email="test@example.com",
            full_name="Test User",
            disabled=False
        )
        logger.info(f"Created mock user with ID: {mock_user.id}")
        
        # Initialize the data ingestion use case
        data_ingestion_usecase = DataIngestionUseCase()
        logger.info("Initialized DataIngestionUseCase")
        
        # Test webpage URL
        webpage_url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
        
        # Create data ingestion with webpage URL
        data_ingestion = await data_ingestion_usecase.submit_data_ingestion(
            title="Python Programming Language",
            specified_text="Information about the Python programming language",
            data_type=DataType.FAQ.value,
            content="Python is a high-level, general-purpose programming language.",
            reference="Wikipedia",
            keywords=["python", "programming", "language"],
            webpage_url=webpage_url,
            user=mock_user
        )
        
        logger.info(f"Created data ingestion with ID: {data_ingestion.id}")
        logger.info(f"Pinecone ID: {data_ingestion.pinecone_id}")
        logger.info(f"Webpage URL: {data_ingestion.webpage_url}")
        
        # Verify that the data was stored in MongoDB
        stored_data = await data_ingestion_repository().get_by_id(data_ingestion.id)
        if stored_data:
            logger.info("✅ Data successfully stored in MongoDB")
            logger.info(f"MongoDB data: {stored_data.dict()}")
        else:
            logger.error("❌ Data not found in MongoDB")
        
        # Search for the data in Pinecone
        search_results = await data_ingestion_usecase.search_data_ingestion(
            query="Python programming language",
            skip=0,
            limit=5,
            user=mock_user
        )
        
        if search_results:
            logger.info("✅ Data successfully found in Pinecone search")
            logger.info(f"Number of search results: {len(search_results)}")
            
            # Check if our data is in the results
            found = False
            for result in search_results:
                if result.get("id") == data_ingestion.id:
                    found = True
                    logger.info(f"Found our data in search results with score: {result.get('similarity_score')}")
                    break
            
            if not found:
                logger.warning("⚠️ Our data was not in the top search results")
        else:
            logger.error("❌ No search results found in Pinecone")
        
        logger.info("Data ingestion test with webpage URL completed")
        
    except Exception as e:
        logger.error(f"Error testing data ingestion with webpage URL: {str(e)}")
        raise

async def main():
    """Main function."""
    try:
        await test_data_ingestion_with_webpage()
        logger.info("Test completed successfully")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 