from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class IFileRepository(ABC):
    """Interface for file repository operations"""
    
    @abstractmethod
    async def upload(self, file_name: str, folder_path: str, file_data: bytes) -> Dict[str, Any]:
        """
        Upload a file to storage
        
        Args:
            file_name: Name of the file
            folder_path: Path to store the file
            file_data: Binary data of the file
            
        Returns:
            Dict containing file information including URL
        """
        pass
    
    @abstractmethod
    async def get(self, file_name: str) -> bytes:
        """
        Get a file from storage
        
        Args:
            file_name: Name of the file to retrieve
            
        Returns:
            Binary data of the file
        """
        pass
    
    @abstractmethod
    async def delete(self, file_name: str) -> bool:
        """
        Delete a file from storage
        
        Args:
            file_name: Name of the file to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        pass 