#!/usr/bin/env python3
"""
Script to test data ingestion with file URLs.
This script tests the file URL handling functionality without connecting to external services.
"""

import asyncio
import logging
import sys
import os
import tempfile
import requests
from pathlib import Path
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Supported file types
SUPPORTED_FILE_TYPES = ["pdf", "docx", "doc", "txt"]

async def download_and_process_file(file_url: str) -> Dict[str, Any]:
    """Download and process a file from a URL."""
    try:
        logger.info(f"Testing file URL handling for: {file_url}")
        
        # Determine file type from URL
        file_extension = file_url.split(".")[-1].lower()
        
        if file_extension not in SUPPORTED_FILE_TYPES:
            logger.error(f"Unsupported file type: {file_extension}")
            raise ValueError(f"Unsupported file type: {file_extension}. Supported types are: {', '.join(SUPPORTED_FILE_TYPES)}")
        
        # Download the file to a temporary location
        with tempfile.NamedTemporaryFile(suffix=f".{file_extension}", delete=False) as temp_file:
            response = requests.get(file_url, stream=True)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            
            temp_file_path = temp_file.name
        
        logger.info(f"File downloaded to temporary location: {temp_file_path}")
        
        # Get file size
        file_size = os.path.getsize(temp_file_path)
        
        # Get file name
        file_name = os.path.basename(file_url)
        
        # Simulate metadata that would be stored in Pinecone
        metadata = {
            "mongodb_id": "mock_id_12345",
            "title": "Test File URL Ingestion",
            "specified_text": "This is a test of file URL ingestion",
            "data_type": "FAQ",
            "content": "This is the content of the test data ingestion",
            "reference": "Test reference",
            "file_url": file_url,
            "file_name": file_name,
            "file_type": file_extension,
            "file_size": file_size,
            "user_id": "test_user_id"
        }
        
        logger.info(f"Metadata that would be stored in Pinecone: {metadata}")
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        logger.info(f"Cleaned up temporary file: {temp_file_path}")
        
        return metadata
        
    except Exception as e:
        logger.error(f"Error processing file URL: {str(e)}")
        raise

async def test_file_url_handling():
    """Test file URL handling functionality."""
    try:
        # Test PDF file
        test_pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
        
        # Process the file URL
        metadata = await download_and_process_file(test_pdf_url)
        
        logger.info("File URL handling test completed successfully")
        logger.info(f"File URL: {metadata['file_url']}")
        logger.info(f"File Name: {metadata['file_name']}")
        logger.info(f"File Type: {metadata['file_type']}")
        logger.info(f"File Size: {metadata['file_size']} bytes")
        
        # Simulate what would happen in the DataIngestionUseCase
        logger.info("\nIn the DataIngestionUseCase, the following would happen:")
        logger.info("1. The file URL would be stored in the DataIngestion model")
        logger.info("2. The file URL would be included in the metadata sent to Pinecone")
        logger.info("3. The file would be downloaded and processed using the load_file_from_url method")
        logger.info("4. The file content would be chunked and stored in Pinecone")
        logger.info("5. The file URL would be included in search results")
        
    except Exception as e:
        logger.error(f"Error testing file URL handling: {str(e)}")
        raise

async def main():
    """Main function."""
    logger.info("Starting file URL handling test...")
    await test_file_url_handling()
    logger.info("File URL handling test completed")

if __name__ == "__main__":
    asyncio.run(main()) 