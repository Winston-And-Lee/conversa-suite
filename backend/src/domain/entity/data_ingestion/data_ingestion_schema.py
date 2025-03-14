from typing import List, Optional, Any, Dict
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

# List data ingestion response class
class ListDataIngestionResponse(BaseModel):
    """Response class for process_list_data_ingestion method."""
    data: List[DataIngestion]
    page: int
    page_size: int
    total_page: int
    total_data: int
    
    class Config:
        arbitrary_types_allowed = True

# Schema definition for AutoRenderFilterV2 component
def get_data_ingestion_schema() -> Dict[str, Any]:
    """
    Generate schema definition for data ingestion model.
    This schema is used by the AutoRenderFilterV2 component in the frontend.
    
    Returns:
        Dict[str, Any]: Schema definition
    """
    return {
        "main": {
            "fields": [
                {
                    "name": "title",
                    "type": "string",
                    "label": "หัวข้อ"
                },
                {
                    "name": "data_type",
                    "type": "enum",
                    "label": "ประเภทข้อมูล",
                    "enum_values": ["ตัวบทกฎหมาย", "FAQ", "FICTION", "คำแนะนำ"]
                },
                {
                    "name": "keywords",
                    "type": "array",
                    "label": "คีย์เวิร์ด"
                },
                {
                    "name": "created_at",
                    "type": "datetime",
                    "label": "วันที่สร้าง"
                },
                {
                    "name": "updated_at",
                    "type": "datetime",
                    "label": "วันที่แก้ไข"
                }
            ]
        }
    } 