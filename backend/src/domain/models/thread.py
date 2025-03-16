"""
Thread models for the application.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ThreadModel(BaseModel):
    """Model for storing thread information in MongoDB."""
    model_config = ConfigDict(populate_by_name=True)
    
    thread_id: str
    user_id: str
    title: str
    summary: str
    messages: List[Dict[str, Any]]
    system_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_archived: bool = False
    state: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get an attribute by key, similar to dictionary get method.
        
        Args:
            key: The attribute name to get
            default: The default value to return if the attribute doesn't exist
            
        Returns:
            The attribute value or default if not found
        """
        return getattr(self, key, default)


class ThreadListResponse(BaseModel):
    """Response model for listing threads."""
    model_config = ConfigDict(populate_by_name=True)
    
    threads: List[ThreadModel] 