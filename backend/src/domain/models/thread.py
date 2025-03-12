"""
Thread models for the application.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ThreadModel(BaseModel):
    """Model for storing thread information in MongoDB."""
    thread_id: str
    user_id: str
    title: str
    summary: str
    messages: List[Dict[str, Any]]
    system_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_archived: bool = False


class ThreadListResponse(BaseModel):
    """Response model for listing threads."""
    threads: List[ThreadModel] 