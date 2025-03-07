from src.interface.repository.database.db_repository import s3_repository
from fastapi import UploadFile

class S3Service:
    """Service for interacting with AWS S3 storage."""

    def __init__(self):
        """Initialize the S3 service with the S3 repository."""
        self.s3_repository = s3_repository()
    
    async def upload_file(self, file: UploadFile) -> dict:
        """
        Upload a file to S3.
        
        Args:
            file: The file to upload
            
        Returns:
            dict: Dictionary containing file URL, name, type, and size
        """
        return await self.s3_repository.upload_file(file)
        
    async def delete_file(self, file_url: str) -> bool:
        """
        Delete a file from S3.
        
        Args:
            file_url: The URL of the file to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        return await self.s3_repository.delete_file(file_url) 