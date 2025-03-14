import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from datetime import datetime
import io

from src.domain.models.user import User
from src.domain.models.file import FileResource, FileType
from src.domain.entity.common import StandardizedResponse, get_schema_field
from src.infrastructure.fastapi.routes.user_routes import get_current_user
from src.usecase.file import get_file_usecase, IFileUseCase

# Create a logger for this module
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Create dependency for file_usecase
def get_file_usecase_dependency() -> IFileUseCase:
    """Dependency that provides the file usecase"""
    return get_file_usecase()

# Response models
class FileResponseModel(BaseModel):
    """Response model for file operations"""
    id: Optional[str] = None
    file_name: str
    file_url: str
    file_type: FileType
    description: Optional[str] = None
    user_create: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class FileListResponse(BaseModel):
    """Response model for file list operations"""
    items: List[FileResponseModel]
    total: int
    limit: int
    offset: int
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

def get_file_schema() -> Dict[str, Any]:
    """Get schema for file resources for frontend filtering"""
    return {
        "file_name": get_schema_field("file_name", "string", "File Name"),
        "file_type": get_schema_field("file_type", "enum", "File Type", [
            {"value": "image", "label": "Image"},
            {"value": "document", "label": "Document"},
            {"value": "audio", "label": "Audio"},
            {"value": "video", "label": "Video"},
            {"value": "other", "label": "Other"}
        ]),
        "description": get_schema_field("description", "string", "Description"),
        "created_at": get_schema_field("created_at", "datetime", "Created At"),
        "updated_at": get_schema_field("updated_at", "datetime", "Updated At")
    }

@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=FileResponseModel)
async def upload_file(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    file_usecase: IFileUseCase = Depends(get_file_usecase_dependency)
):
    """
    Upload a file to storage
    
    Args:
        file: The file to upload
        description: Optional description of the file
        current_user: Current authenticated user
        file_usecase: File usecase dependency
        
    Returns:
        FileResponseModel object
    """
    try:
        # Read file data
        file_data = await file.read()
        
        # Upload file
        file_resource = await file_usecase.upload_file(current_user, file.filename, file_data)
        
        # Update description if provided
        if description and hasattr(file_resource, 'description'):
            file_resource.description = description
            # TODO: Update file resource in database
        
        return file_resource
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@router.get("", response_model=StandardizedResponse[FileResource])
async def list_files(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _page: Optional[int] = None,
    _pageSize: Optional[int] = None,
    _sort: Optional[str] = None,
    _order: Optional[str] = None,
    file_name: Optional[str] = None,
    file_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    file_usecase: IFileUseCase = Depends(get_file_usecase_dependency)
):
    """
    List files for the current user
    
    Args:
        limit: Maximum number of files to return
        offset: Offset for pagination
        _page: Alternative page parameter (used by refine)
        _pageSize: Alternative page size parameter (used by refine)
        _sort: Field to sort by (used by refine)
        _order: Sort order (asc or desc, used by refine)
        file_name: Optional filter for file name
        file_type: Optional filter for file type
        current_user: Current authenticated user
        file_usecase: File usecase dependency
        
    Returns:
        StandardizedResponse object
    """
    try:
        # Handle refine pagination parameters
        page = _page if _page is not None else (offset // limit) + 1
        page_size = _pageSize if _pageSize is not None else limit
        
        # Calculate offset from page if provided
        if _page is not None:
            offset = (page - 1) * page_size
        
        # Create filter parameters
        filter_params = {"user_create": current_user.email}
        
        # Add additional filters if provided
        if file_name:
            filter_params["file_name"] = {"$regex": file_name, "$options": "i"}
        
        if file_type:
            filter_params["file_type"] = file_type
        
        # Determine sort parameters
        sort_params = []
        if _sort and _order:
            direction = -1 if _order.lower() == 'desc' else 1
            sort_params = [(_sort, direction)]
        else:
            # Default sort by created_at descending
            sort_params = [("created_at", -1)]
        
        # Get resources and count
        resources, total = await file_usecase.get_file_resources(
            current_user, 
            limit=page_size, 
            offset=offset,
            filter_params=filter_params,
            sort_params=sort_params
        )
        
        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        
        # Get schema for frontend filtering
        data_schema = get_file_schema()
        
        # Return standardized response
        return StandardizedResponse[FileResource](
            code=0,
            message="",
            data=resources,
            page=page,
            page_size=page_size,
            total_page=total_pages,
            total_data=total,
            data_schema=data_schema
        )
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@router.get("/download/{file_name:path}")
async def download_file(
    file_name: str,
    current_user: User = Depends(get_current_user),
    file_usecase: IFileUseCase = Depends(get_file_usecase_dependency)
):
    """
    Download a file
    
    Args:
        file_name: Name of the file to download
        current_user: Current authenticated user
        file_usecase: File usecase dependency
        
    Returns:
        StreamingResponse with file data
    """
    try:
        # Get file data
        file_data = await file_usecase.get_file(file_name)
        
        # Determine content type
        content_type = "application/octet-stream"
        if file_name.endswith(".pdf"):
            content_type = "application/pdf"
        elif file_name.endswith((".jpg", ".jpeg")):
            content_type = "image/jpeg"
        elif file_name.endswith(".png"):
            content_type = "image/png"
        
        # Create response
        return StreamingResponse(
            io.BytesIO(file_data),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={file_name.split('/')[-1]}"}
        )
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")

@router.delete("/{file_name:path}")
async def delete_file(
    file_name: str,
    current_user: User = Depends(get_current_user),
    file_usecase: IFileUseCase = Depends(get_file_usecase_dependency)
):
    """
    Delete a file
    
    Args:
        file_name: Name of the file to delete
        current_user: Current authenticated user
        file_usecase: File usecase dependency
        
    Returns:
        Success message
    """
    try:
        deleted = await file_usecase.delete_file(current_user, file_name)
        if deleted:
            return {"message": "File deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="File not found or could not be deleted")
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}") 