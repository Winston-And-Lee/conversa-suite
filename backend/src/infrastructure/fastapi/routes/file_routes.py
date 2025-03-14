import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from datetime import datetime
import io

from src.domain.models.user import User
from src.domain.models.file import FileResource, FileType
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

@router.get("/list", response_model=FileListResponse)
async def list_files(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    file_usecase: IFileUseCase = Depends(get_file_usecase_dependency)
):
    """
    List files for the current user
    
    Args:
        limit: Maximum number of files to return
        offset: Offset for pagination
        current_user: Current authenticated user
        file_usecase: File usecase dependency
        
    Returns:
        FileListResponse object
    """
    try:
        resources, total = await file_usecase.get_file_resources(current_user, limit, offset)
        return {
            "items": resources,
            "total": total,
            "limit": limit,
            "offset": offset
        }
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