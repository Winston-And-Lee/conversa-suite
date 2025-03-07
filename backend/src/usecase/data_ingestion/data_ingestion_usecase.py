import logging
import os
from typing import List, Dict, Any, Optional
from fastapi import UploadFile, HTTPException

from src.domain.models.data_ingestion import DataIngestion, DataType
from src.infrastructure.services.text_extraction_service import TextExtractionService
from src.interface.repository.database.db_repository import data_ingestion_repository, s3_repository, pinecone_repository


class DataIngestionUseCase:
    """Use case for handling data ingestion operations."""

    def __init__(self):
        """Initialize with required repositories and services."""
        # Get repositories through factory functions
        self.data_ingestion_repository = data_ingestion_repository()
        self.s3_repository = s3_repository()
        self.pinecone_repository = pinecone_repository()
        
        # Initialize services
        self.text_extraction_service = TextExtractionService()
        self.logger = logging.getLogger(__name__)
    
    async def submit_data_ingestion(
        self,
        title: str,
        specified_text: str,
        data_type: str,
        law: str,
        reference: str,
        keywords: List[str],
        file: Optional[UploadFile] = None
    ) -> DataIngestion:
        """
        Submit data ingestion with file upload.
        
        Args:
            title: Title
            specified_text: Specified text
            data_type: Data type (ตัวบทกฎหมาย, FAQ, คำแนะนำ)
            law: Law/regulation
            reference: Reference
            keywords: Keywords list
            file: Optional uploaded file
            
        Returns:
            DataIngestion: Created data ingestion with IDs
        """
        try:
            # Create a DataIngestion instance
            data_ingestion = DataIngestion(
                title=title,
                specified_text=specified_text,
                data_type=data_type,
                law=law,
                reference=reference,
                keywords=keywords
            )
            
            # Handle file upload if provided
            file_text = ""
            if file:
                # Upload file to S3
                file_info = await self.s3_repository.upload_file(file)
                
                # Add file info to data_ingestion
                data_ingestion.file_url = file_info["file_url"]
                data_ingestion.file_name = file_info["file_name"]
                data_ingestion.file_type = file_info["file_type"]
                data_ingestion.file_size = file_info["file_size"]
                
                # Extract text from file
                file_text = await self.text_extraction_service.extract_from_url(
                    file_info["file_url"],
                    file_info["file_type"]
                )
            
            # If keywords are empty, generate them
            if not keywords:
                # Combine title, specified_text, and file_text for keyword generation
                combined_text = f"{title} {specified_text} {file_text}"
                generated_keywords = await self.pinecone_repository.generate_keywords(combined_text)
                data_ingestion.keywords = generated_keywords
            
            # Save to MongoDB
            created_data_ingestion = await self.data_ingestion_repository.create(data_ingestion)
            
            # Create metadata for Pinecone
            metadata = {
                "mongodb_id": created_data_ingestion.id,
                "title": title,
                "specified_text": specified_text,
                "data_type": data_type,
                "law": law,
                "reference": reference,
                "has_file": bool(file)
            }
            
            # Create text data for embedding
            text_data = {
                "title": title,
                "specified_text": specified_text,
                "keywords": created_data_ingestion.keywords,
                "file_text": file_text
            }
            
            # Store in Pinecone
            pinecone_id = await self.pinecone_repository.upsert_vector(text_data, metadata)
            
            # Update DataIngestion with Pinecone ID
            await self.data_ingestion_repository.update(
                created_data_ingestion.id,
                {"pinecone_id": pinecone_id}
            )
            created_data_ingestion.pinecone_id = pinecone_id
            
            return created_data_ingestion
            
        except Exception as e:
            self.logger.error(f"Data ingestion submission error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Data ingestion submission error: {str(e)}")
    
    async def get_data_ingestion(self, data_id: str) -> DataIngestion:
        """
        Get data ingestion by ID.
        
        Args:
            data_id: Data ingestion ID
            
        Returns:
            DataIngestion: Retrieved data ingestion
        """
        data_ingestion = await self.data_ingestion_repository.get_by_id(data_id)
        
        if not data_ingestion:
            raise HTTPException(status_code=404, detail="Data ingestion not found")
        
        return data_ingestion
    
    async def search_data_ingestion(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search data ingestion by query text.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: Search results
        """
        try:
            # Perform semantic search in Pinecone
            search_results = await self.pinecone_repository.semantic_search(query, limit)
            
            return search_results
            
        except Exception as e:
            self.logger.error(f"Search error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")
    
    async def delete_data_ingestion(self, data_id: str) -> bool:
        """
        Delete data ingestion and associated resources.
        
        Args:
            data_id: Data ingestion ID
            
        Returns:
            bool: True if deletion successful
        """
        # Get data ingestion
        data_ingestion = await self.data_ingestion_repository.get_by_id(data_id)
        
        if not data_ingestion:
            raise HTTPException(status_code=404, detail="Data ingestion not found")
        
        # Delete from Pinecone if ID exists
        if data_ingestion.pinecone_id:
            await self.pinecone_repository.delete_vector(data_ingestion.pinecone_id)
        
        # Delete file from S3 if URL exists
        if data_ingestion.file_url:
            await self.s3_repository.delete_file(data_ingestion.file_url)
        
        # Delete from MongoDB
        deleted = await self.data_ingestion_repository.delete(data_id)
        
        return deleted 