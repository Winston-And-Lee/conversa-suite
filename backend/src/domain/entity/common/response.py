from typing import List, Dict, Any, Optional, TypeVar, Generic
from pydantic import BaseModel
from datetime import datetime

# Generic type for data
T = TypeVar('T')

class StandardizedResponse(BaseModel, Generic[T]):
    """
    Standardized response format for API endpoints.
    This is a generic class that can be used with any data type.
    
    Attributes:
        code: Response code (0 for success, non-zero for errors)
        message: Response message
        data: Response data (list of items)
        page: Current page number
        page_size: Number of items per page
        total_page: Total number of pages
        total_data: Total number of items
        data_schema: Optional schema information for frontend filtering/rendering
    """
    code: int = 0
    message: str = ""
    data: List[T]
    page: int
    page_size: int
    total_page: int
    total_data: int
    data_schema: Optional[Dict[str, Any]] = None
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class SingleItemResponse(BaseModel, Generic[T]):
    """
    Standardized response format for single item API endpoints.
    This is a generic class that can be used with any data type.
    
    Attributes:
        code: Response code (0 for success, non-zero for errors)
        message: Response message
        data: Response data (single item)
        data_schema: Optional schema information for frontend rendering
    """
    code: int = 0
    message: str = ""
    data: T
    data_schema: Optional[Dict[str, Any]] = None
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


def get_schema_field(field_name: str, field_type: str, label: str, options: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Helper function to create a schema field definition
    
    Args:
        field_name: Name of the field
        field_type: Type of the field (string, enum, datetime, etc.)
        label: Display label for the field
        options: Optional list of options for enum fields
        
    Returns:
        Dictionary with field schema definition
    """
    schema = {
        "type": field_type,
        "label": label
    }
    
    if options:
        schema["options"] = options
        
    return schema 