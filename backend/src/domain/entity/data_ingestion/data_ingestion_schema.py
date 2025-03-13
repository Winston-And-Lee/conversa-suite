from typing import List, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from src.domain.models.data_ingestion import DataIngestion, DataType

# Enum for data types
class DataTypeEnum(str, Enum):
    LEGAL_TEXT = "ตัวบทกฎหมาย"  # Legal Text/Article
    FAQ = "FAQ"                  # FAQ
    RECOMMENDATION = "คำแนะนำ"   # Recommendation/Advice
    FICTION = "FICTION"          # Fiction/Stories
    
# Search request schema
class SearchRequest(BaseModel):
    query: Optional[str] = Field(default="", description="Text query to search for")
    page: int = Field(default=1, description="Page number")
    page_size: int = Field(default=10, description="Number of items per page")
    
# Standard API response format
class StandardResponse(BaseModel):
    code: int = 0
    message: str = ""
    data: Any
    page: Optional[int] = None
    page_size: Optional[int] = None
    total_page: Optional[int] = None
    total_data: Optional[int] = None
    data_schema: Optional[Any] = None
    
# Search response schema
class SearchResponse(StandardResponse):
    data: List[DataIngestion] 