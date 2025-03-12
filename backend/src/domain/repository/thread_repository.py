"""
Thread repository interface for thread operations.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.domain.models.thread import ThreadModel


class ThreadRepository:
    """Interface for thread repository operations."""
    
    async def create_thread(self, thread_data: Dict[str, Any]) -> str:
        """
        Create a new thread.
        
        Args:
            thread_data: The thread data to create
            
        Returns:
            The ID of the created thread
        """
        raise NotImplementedError
    
    async def get_thread(self, thread_id: str) -> Optional[ThreadModel]:
        """
        Get a thread by ID.
        
        Args:
            thread_id: The ID of the thread to get
            
        Returns:
            The thread or None if not found
        """
        raise NotImplementedError
    
    async def update_thread(self, thread_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update a thread.
        
        Args:
            thread_id: The ID of the thread to update
            update_data: The data to update
            
        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError
    
    async def delete_thread(self, thread_id: str) -> bool:
        """
        Delete a thread.
        
        Args:
            thread_id: The ID of the thread to delete
            
        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError
    
    async def list_threads_by_user(self, user_id: str, limit: int = 20, skip: int = 0) -> List[ThreadModel]:
        """
        List threads by user ID.
        
        Args:
            user_id: The ID of the user
            limit: The maximum number of threads to return
            skip: The number of threads to skip
            
        Returns:
            A list of threads
        """
        raise NotImplementedError
    
    async def add_message_to_thread(self, thread_id: str, message: Dict[str, Any]) -> bool:
        """
        Add a message to a thread.
        
        Args:
            thread_id: The ID of the thread
            message: The message to add
            
        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError
    
    async def update_thread_summary(self, thread_id: str, summary: str) -> bool:
        """
        Update the summary of a thread.
        
        Args:
            thread_id: The ID of the thread
            summary: The new summary
            
        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError 