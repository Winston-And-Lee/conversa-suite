import logging
import uuid
import os
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
import mimetypes
from pathlib import Path

from src.domain.models.file import FileResource, FileType
from src.domain.models.user import User
from src.domain.repository.file_repository import IFileRepository
from src.interface.repository.database.db_repository import file_repository, file_resource_repository

logger = logging.getLogger(__name__)

class IFileUseCase:
    """Interface for file use cases"""
    
    async def upload_file(self, user: User, file_name: str, file_data: bytes) -> FileResource:
        """Upload a file and create a file resource"""
        pass
    
    async def get_file(self, file_name: str) -> bytes:
        """Get a file by name"""
        pass
    
    async def delete_file(self, user: User, file_name: str) -> bool:
        """Delete a file by name"""
        pass
    
    async def get_file_resources(self, user: User, limit: int = 10, offset: int = 0) -> Tuple[List[FileResource], int]:
        """Get file resources for a user"""
        pass

class FileUseCase(IFileUseCase):
    """Implementation of file use cases"""
    
    def __init__(self, file_repo_instance: Optional[IFileRepository] = None):
        """Initialize with optional repository dependency"""
        self.file_repo = file_repo_instance or file_repository()
        self.file_resource_repo = file_resource_repository()
    
    async def upload_file(self, user: User, file_name: str, file_data: bytes) -> FileResource:
        """
        Upload a file and create a file resource
        
        Args:
            user: Current user
            file_name: Name of the file
            file_data: Binary data of the file
            
        Returns:
            FileResource object
        """
        # Generate a unique ID for the file name
        unique_id = uuid.uuid4().hex[:8]
        
        # Get current date for folder structure
        now = datetime.utcnow()
        year, month, day = now.year, now.month, now.day
        
        # Extract file extension
        file_extension = os.path.splitext(file_name)[1]
        
        # Create new file name with unique ID
        base_name = os.path.splitext(file_name)[0]
        new_file_name = f"{base_name}_{unique_id}{file_extension}"
        
        # Create folder path
        folder_path = f"files/{year}/{month:02d}/{day:02d}"
        
        # Upload file to storage
        try:
            file_entity = await self.file_repo.upload(new_file_name, folder_path, file_data)
            
            # Determine file type based on extension
            file_type = self._determine_file_type(file_extension)
            
            # Create file resource
            file_resource = FileResource(
                file_name=f"{folder_path}/{new_file_name}",
                file_url=file_entity["URL"],
                file_type=file_type,
                user_create=user.email,
                created_at=now,
                updated_at=now
            )
            
            # Save to database
            saved_resource = await self.file_resource_repo.create(file_resource)
            return saved_resource
            
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise Exception(f"Failed to upload file: {str(e)}")
    
    async def get_file(self, file_name: str) -> bytes:
        """
        Get a file by name
        
        Args:
            file_name: Name of the file
            
        Returns:
            Binary data of the file
        """
        try:
            return await self.file_repo.get(file_name)
        except Exception as e:
            logger.error(f"Error getting file: {str(e)}")
            raise Exception(f"Failed to get file: {str(e)}")
    
    async def delete_file(self, user: User, file_name: str) -> bool:
        """
        Delete a file by name
        
        Args:
            user: Current user
            file_name: Name of the file
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            # Delete from storage
            deleted = await self.file_repo.delete(file_name)
            
            if deleted:
                # Delete from database
                await self.file_resource_repo.delete_by_filter({
                    "file_name": file_name,
                    "user_create": user.email
                })
            
            return deleted
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False
    
    async def get_file_resources(self, user: User, limit: int = 10, offset: int = 0) -> Tuple[List[FileResource], int]:
        """
        Get file resources for a user
        
        Args:
            user: Current user
            limit: Maximum number of resources to return
            offset: Offset for pagination
            
        Returns:
            Tuple of (list of FileResource objects, total count)
        """
        try:
            filter_params = {"user_create": user.email}
            resources = await self.file_resource_repo.find(
                filter_params, 
                limit=limit, 
                offset=offset, 
                sort=[("created_at", -1)]
            )
            count = await self.file_resource_repo.count(filter_params)
            return resources, count
        except Exception as e:
            logger.error(f"Error getting file resources: {str(e)}")
            return [], 0
    
    def _determine_file_type(self, extension: str) -> FileType:
        """
        Determine file type based on extension
        
        Args:
            extension: File extension
            
        Returns:
            FileType enum value
        """
        extension = extension.lower()
        
        # Image types
        if extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.svg', '.ico']:
            return FileType.IMAGE
        
        # Document types
        if extension in ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx', '.csv']:
            return FileType.DOCUMENT
        
        # Audio types
        if extension in ['.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a']:
            return FileType.AUDIO
        
        # Video types
        if extension in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv']:
            return FileType.VIDEO
        
        # Default
        return FileType.OTHER

def get_file_usecase() -> IFileUseCase:
    """Factory function to create a file usecase instance"""
    return FileUseCase() 