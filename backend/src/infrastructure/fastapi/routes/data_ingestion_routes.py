from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse

from src.domain.models.data_ingestion import DataType
from src.domain.entity.data_ingestion import (
    DataIngestionRequest,
    DataIngestionResponse,
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    DataTypeEnum
)
from src.usecase.data_ingestion import DataIngestionUseCase
from src.interface.repository.mongodb.data_ingestion_repository import DataIngestionRepository
from src.infrastructure.services.s3_service import S3Service
from src.infrastructure.services.text_extraction_service import TextExtractionService
from src.infrastructure.services.pinecone_service import PineconeService
from src.config.database import get_database


router = APIRouter(
    prefix="/api/data-ingestion",
    tags=["Data Ingestion"]
)


async def get_data_ingestion_usecase():
    """Dependency for data ingestion use case."""
    return DataIngestionUseCase()


@router.post(
    "/",
    response_model=DataIngestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit data ingestion with file"
)
async def submit_data_ingestion(
    title: str = Form(..., description="หัวข้อ (Heading/Title)"),
    specified_text: str = Form(..., description="ระบุ (Specify)"),
    data_type: DataTypeEnum = Form(..., description="ประเภทข้อมูล (Data Type)"),
    law: str = Form(..., description="กฎหมาย (Law/Regulation)"),
    reference: str = Form(..., description="อ้างอิง (Reference)"),
    keywords: List[str] = Form(default=[], description="คีย์เวิร์ด (Keywords)"),
    file: Optional[UploadFile] = File(None, description="เอกสารแนบ (PDF/DOC, max 10MB)"),
    data_ingestion_usecase: DataIngestionUseCase = Depends(get_data_ingestion_usecase)
):
    """
    Submit data ingestion with file upload.
    
    - **title**: หัวข้อ (Heading/Title)
    - **specified_text**: ระบุ (Specify text content)
    - **data_type**: ประเภทข้อมูล (Data type - Legal text, FAQ, or Recommendation)
    - **law**: กฎหมาย (Law/Regulation)
    - **reference**: อ้างอิง (Reference)
    - **keywords**: คีย์เวิร์ด (Keywords, optional)
    - **file**: File upload (PDF or DOC, maximum 10MB)
    """
    try:
        data_ingestion = await data_ingestion_usecase.submit_data_ingestion(
            title=title,
            specified_text=specified_text,
            data_type=data_type.value,  # Convert enum to string value
            law=law,
            reference=reference,
            keywords=keywords,
            file=file
        )
        
        # Convert data_ingestion object to response model
        return DataIngestionResponse(
            id=data_ingestion.id,
            title=data_ingestion.title,
            specified_text=data_ingestion.specified_text,
            data_type=data_ingestion.data_type,
            law=data_ingestion.law,
            reference=data_ingestion.reference,
            keywords=data_ingestion.keywords,
            file_url=data_ingestion.file_url,
            file_name=data_ingestion.file_name,
            file_type=data_ingestion.file_type,
            file_size=data_ingestion.file_size,
            created_at=data_ingestion.created_at,
            updated_at=data_ingestion.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{data_id}",
    response_model=DataIngestionResponse,
    summary="Get data ingestion by ID"
)
async def get_data_ingestion(
    data_id: str,
    data_ingestion_usecase: DataIngestionUseCase = Depends(get_data_ingestion_usecase)
):
    """
    Get data ingestion by ID.
    
    - **data_id**: Data ingestion ID
    """
    try:
        data_ingestion = await data_ingestion_usecase.get_data_ingestion(data_id)
        
        return DataIngestionResponse(
            id=data_ingestion.id,
            title=data_ingestion.title,
            specified_text=data_ingestion.specified_text,
            data_type=data_ingestion.data_type,
            law=data_ingestion.law,
            reference=data_ingestion.reference,
            keywords=data_ingestion.keywords,
            file_url=data_ingestion.file_url,
            file_name=data_ingestion.file_name,
            file_type=data_ingestion.file_type,
            file_size=data_ingestion.file_size,
            created_at=data_ingestion.created_at,
            updated_at=data_ingestion.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/search",
    response_model=SearchResponse,
    summary="Search data ingestion"
)
async def search_data_ingestion(
    search_request: SearchRequest,
    data_ingestion_usecase: DataIngestionUseCase = Depends(get_data_ingestion_usecase)
):
    """
    Search data ingestion using text query.
    
    - **query**: Search query text
    - **limit**: Maximum number of results (default: 10)
    """
    try:
        search_results = await data_ingestion_usecase.search_data_ingestion(
            query=search_request.query,
            limit=search_request.limit
        )
        
        # Convert to response model
        results = [
            SearchResultItem(
                id=result["id"],
                title=result["title"],
                specified_text=result["specified_text"],
                data_type=result["data_type"],
                similarity_score=result["similarity_score"]
            )
            for result in search_results
        ]
        
        return SearchResponse(
            results=results,
            total=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{data_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete data ingestion"
)
async def delete_data_ingestion(
    data_id: str,
    data_ingestion_usecase: DataIngestionUseCase = Depends(get_data_ingestion_usecase)
):
    """
    Delete data ingestion and associated resources.
    
    - **data_id**: Data ingestion ID
    """
    try:
        deleted = await data_ingestion_usecase.delete_data_ingestion(data_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Data ingestion not found")
        
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting data ingestion: {str(e)}") 