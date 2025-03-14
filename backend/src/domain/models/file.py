from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field


class FileType(str, Enum):
    """Enum for file types"""
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    OTHER = "other"


class FileResource(BaseModel):
    """Model for file resources"""
    id: Optional[str] = Field(None, alias="_id")
    file_name: str
    file_url: str
    file_type: FileType = FileType.OTHER
    description: Optional[str] = None
    user_create: str
    meta_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        } 