from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DataType(str, Enum):
    """Enum for data types in Thai form."""
    LEGAL_TEXT = "ตัวบทกฎหมาย"  # Legal Text/Article
    FAQ = "FAQ"                  # FAQ
    RECOMMENDATION = "คำแนะนำ"   # Recommendation/Advice


class DataIngestion(BaseModel):
    """Domain model for data ingestion."""
    id: Optional[str] = None
    title: str  # หัวข้อ (Heading/Title)
    specified_text: str  # ระบุ (Specify)
    data_type: DataType  # ประเภทข้อมูล (Data Type)
    law: str  # กฎหมาย (Law/Regulation)
    reference: str  # อ้างอิง (Reference)
    keywords: List[str]  # คีย์เวิร์ด (Keywords)
    file_url: Optional[str] = None  # S3 URL for uploaded file
    file_name: Optional[str] = None  # Original filename
    file_type: Optional[str] = None  # File type (PDF or DOC)
    file_size: Optional[int] = None  # File size in bytes
    pinecone_id: Optional[str] = None  # Vector ID in Pinecone
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True 