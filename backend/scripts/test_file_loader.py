#!/usr/bin/env python3
"""
Script to test the file loading functionality without connecting to Pinecone.
This script tests downloading and processing files from URLs.
"""

import asyncio
import logging
import sys
import os
import tempfile
import requests
from pathlib import Path
from typing import List, Dict, Any

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredFileLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Supported file types
SUPPORTED_FILE_TYPES = ["pdf", "docx", "doc", "txt"]

async def download_file(file_url: str) -> str:
    """Download a file from a URL to a temporary location."""
    try:
        logger.info(f"Downloading file from URL: {file_url}")
        
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
        return temp_file_path
        
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise

async def process_file(file_path: str) -> Dict[str, Any]:
    """Process a file and extract information."""
    try:
        logger.info(f"Processing file: {file_path}")
        
        # Get file extension
        file_extension = Path(file_path).suffix.lower()[1:]
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Get file name
        file_name = os.path.basename(file_path)
        
        # Load the document based on file type
        if file_extension == "pdf":
            loader = PyPDFLoader(file_path)
        elif file_extension in ["docx", "doc"]:
            loader = Docx2txtLoader(file_path)
        elif file_extension == "txt":
            loader = TextLoader(file_path)
        else:
            # Fallback to unstructured loader
            loader = UnstructuredFileLoader(file_path)
        
        documents = loader.load()
        logger.info(f"Loaded {len(documents)} document(s) from file")
        
        # Split the documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Split documents into {len(chunks)} chunks")
        
        # Log the first chunk content (truncated)
        if chunks:
            first_chunk = chunks[0].page_content
            logger.info(f"First chunk content (truncated): {first_chunk[:100]}...")
        
        # Return file information
        return {
            "file_path": file_path,
            "file_extension": file_extension,
            "file_size": file_size,
            "file_name": file_name,
            "num_documents": len(documents),
            "num_chunks": len(chunks)
        }
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise

async def test_file_loading():
    """Test file loading functionality."""
    try:
        # Test PDF file
        test_pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
        
        # Download the file
        file_path = await download_file(test_pdf_url)
        
        # Process the file
        file_info = await process_file(file_path)
        
        # Log file information
        logger.info(f"File information: {file_info}")
        
        # Clean up
        os.unlink(file_path)
        logger.info(f"Cleaned up temporary file: {file_path}")
        
        logger.info("File loading test completed successfully")
        
    except Exception as e:
        logger.error(f"Error testing file loading: {str(e)}")
        raise

async def main():
    """Main function."""
    logger.info("Starting file loading test...")
    await test_file_loading()
    logger.info("File loading test completed")

if __name__ == "__main__":
    asyncio.run(main()) 