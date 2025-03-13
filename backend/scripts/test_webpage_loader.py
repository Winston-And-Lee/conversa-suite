#!/usr/bin/env python3
"""
Script to test webpage loading functionality without connecting to Pinecone.
This script tests downloading and processing content from web pages.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import List, Dict, Any

from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def load_and_process_webpage(webpage_url: str) -> Dict[str, Any]:
    """Load and process a webpage."""
    try:
        logger.info(f"Testing webpage loading for: {webpage_url}")
        
        # Use WebBaseLoader to load the webpage
        loader = WebBaseLoader(webpage_url)
        documents = loader.load()
        logger.info(f"Loaded {len(documents)} document(s) from webpage")
        
        # Extract webpage title if available
        webpage_title = ""
        if documents and hasattr(documents[0], "metadata") and "title" in documents[0].metadata:
            webpage_title = documents[0].metadata["title"]
            logger.info(f"Extracted webpage title: {webpage_title}")
        
        # Get total content length
        total_content_length = sum(len(doc.page_content) for doc in documents)
        logger.info(f"Total content length: {total_content_length} characters")
        
        # Split the documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Split webpage into {len(chunks)} chunks")
        
        # Log the first chunk content (truncated)
        if chunks:
            first_chunk = chunks[0].page_content
            logger.info(f"First chunk content (truncated): {first_chunk[:100]}...")
        
        # Simulate metadata that would be stored in Pinecone
        metadata = {
            "mongodb_id": "mock_id_12345",
            "title": webpage_title or "Test Webpage Ingestion",
            "specified_text": "This is a test of webpage ingestion",
            "data_type": "FAQ",
            "content": "This is the content of the test data ingestion",
            "reference": webpage_url,
            "webpage_url": webpage_url,
            "source_type": "webpage",
            "user_id": "test_user_id"
        }
        
        logger.info(f"Metadata that would be stored in Pinecone: {metadata}")
        
        # Return webpage information
        return {
            "webpage_url": webpage_url,
            "webpage_title": webpage_title,
            "num_documents": len(documents),
            "num_chunks": len(chunks),
            "total_content_length": total_content_length,
            "metadata": metadata
        }
        
    except Exception as e:
        logger.error(f"Error processing webpage: {str(e)}")
        raise

async def test_webpage_loading():
    """Test webpage loading functionality."""
    try:
        # Test a few different webpages
        test_urls = [
            "https://en.wikipedia.org/wiki/Python_(programming_language)",
            "https://docs.python.org/3/tutorial/index.html"
        ]
        
        for url in test_urls:
            logger.info(f"\n--- Testing URL: {url} ---")
            webpage_info = await load_and_process_webpage(url)
            
            logger.info(f"Webpage URL: {webpage_info['webpage_url']}")
            logger.info(f"Webpage Title: {webpage_info['webpage_title']}")
            logger.info(f"Number of Documents: {webpage_info['num_documents']}")
            logger.info(f"Number of Chunks: {webpage_info['num_chunks']}")
            logger.info(f"Total Content Length: {webpage_info['total_content_length']} characters")
            
        logger.info("\nWebpage loading test completed successfully")
        
        # Simulate what would happen in the PineconeRepository
        logger.info("\nIn the PineconeRepository, the following would happen:")
        logger.info("1. The webpage URL would be detected in the metadata")
        logger.info("2. The webpage content would be loaded using WebBaseLoader")
        logger.info("3. The content would be split into chunks")
        logger.info("4. Each chunk would be embedded and stored in Pinecone")
        logger.info("5. The webpage URL would be included in search results")
        
    except Exception as e:
        logger.error(f"Error testing webpage loading: {str(e)}")
        raise

async def main():
    """Main function."""
    logger.info("Starting webpage loading test...")
    await test_webpage_loading()
    logger.info("Webpage loading test completed")

if __name__ == "__main__":
    asyncio.run(main()) 