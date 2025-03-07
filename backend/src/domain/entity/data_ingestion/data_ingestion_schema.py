from typing import List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

# Enum for data types
class DataTypeEnum(str, Enum):
    LEGAL_TEXT = "ตัวบทกฎหมาย"  # Legal Text/Article
    FAQ = "FAQ"                  # FAQ
    RECOMMENDATION = "คำแนะนำ"   # Recommendation/Advice
    
# Data ingestion request schema (without file)
class DataIngestionRequest(BaseModel):
    title: str = Field(..., description="หัวข้อ (Heading/Title)")
    specified_text: str = Field(..., description="ระบุ (Specify)")
    data_type: DataTypeEnum = Field(..., description="ประเภทข้อมูล (Data Type)")
    law: str = Field(..., description="กฎหมาย (Law/Regulation)")
    reference: str = Field(..., description="อ้างอิง (Reference)")
    keywords: List[str] = Field(default=[], description="คีย์เวิร์ด (Keywords)")

# Data ingestion response schema
class DataIngestionResponse(BaseModel):
    id: str
    title: str
    specified_text: str
    data_type: str
    law: str
    reference: str
    keywords: List[str]
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    created_at: datetime
    updated_at: datetime

# Search request schema
class SearchRequest(BaseModel):
    query: str = Field(..., description="Text query to search for")
    limit: int = Field(default=10, description="Maximum number of results to return")

# Search result item schema
class SearchResultItem(BaseModel):
    id: str
    title: str
    specified_text: str
    data_type: str
    similarity_score: float
    
# Search response schema
class SearchResponse(BaseModel):
    results: List[SearchResultItem]
    total: int 