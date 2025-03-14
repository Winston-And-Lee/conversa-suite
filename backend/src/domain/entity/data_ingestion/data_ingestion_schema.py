from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from src.domain.models.data_ingestion import DataIngestion, DataType
from src.domain.entity.common import StandardizedResponse, get_schema_field

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
        "title": get_schema_field("title", "string", "หัวข้อ"),
        "data_type": get_schema_field("data_type", "enum", "ประเภทข้อมูล", [
            {"value": DataTypeEnum.LEGAL_TEXT, "label": "ตัวบทกฎหมาย"},
            {"value": DataTypeEnum.FAQ, "label": "FAQ"},
            {"value": DataTypeEnum.RECOMMENDATION, "label": "คำแนะนำ"},
            {"value": DataTypeEnum.FICTION, "label": "FICTION"}
        ]),
        "keywords": get_schema_field("keywords", "array", "คีย์เวิร์ด"),
        "created_at": get_schema_field("created_at", "datetime", "วันที่สร้าง"),
        "updated_at": get_schema_field("updated_at", "datetime", "วันที่แก้ไข")
    } 