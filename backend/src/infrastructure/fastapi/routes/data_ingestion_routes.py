from typing import List, Optional, Union
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Body
from fastapi.responses import JSONResponse
import json
from pathlib import Path

from src.domain.models.data_ingestion import DataType, DataIngestion
from src.domain.models.user import User
from src.domain.entity.data_ingestion import (
    SearchRequest,
    SearchResponse,
    DataTypeEnum    
)
from src.usecase.data_ingestion import DataIngestionUseCase
from src.infrastructure.services.s3_service import S3Service
from src.infrastructure.fastapi.routes.user_routes import get_current_user


router = APIRouter(
    prefix="/api/data-ingestion",
    tags=["Data Ingestion"]
)


async def get_data_ingestion_usecase():
    """Dependency for data ingestion use case."""
    return DataIngestionUseCase()


@router.post(
    "/",
    response_model=DataIngestion,
    status_code=status.HTTP_201_CREATED,
    summary="Submit data ingestion with JSON"
)
async def submit_data_ingestion(
    data_ingestion: DataIngestion,
    current_user: User = Depends(get_current_user),
    data_ingestion_usecase: DataIngestionUseCase = Depends(get_data_ingestion_usecase)
):
    """
    Submit data ingestion with JSON payload.
    
    Example request:
    ```json
    {
        "title": "Snow White and the Seven Dwarfs",
        "specified_text": "Mirror, mirror on the wall, who is the fairest of them all?",
        "data_type": "FICTION",
        "content": "Snow White and the Seven Dwarfs is a classic fairy tale...",
        "reference": "The Brothers Grimm, 1812",
        "keywords": ["fairy tale", "princess", "magic mirror", "dwarfs", "poisoned apple"],
        "webpage_url": "https://www.gutenberg.org/files/2591/2591-h/2591-h.htm"
    }
    ```
    
    Fields:
    - **title**: หัวข้อ (Heading/Title)
    - **specified_text**: ระบุ (Specify text content)
    - **data_type**: ประเภทข้อมูล (Data type - Legal text, FAQ, Recommendation, or Fiction)
    - **content**: เนื้อหา (Content, optional)
    - **reference**: อ้างอิง (Reference)
    - **keywords**: คีย์เวิร์ด (Keywords, optional)
    - **file_url**: URL to a file (optional)
    - **webpage_url**: URL to a webpage (optional)
    """
    try:
        # Submit the data ingestion
        result = await data_ingestion_usecase.submit_data_ingestion(
            data_ingestion=data_ingestion,
            user=current_user
        )
        
        # Return the data_ingestion object directly
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{data_id}",
    response_model=DataIngestion,
    summary="Get data ingestion by ID"
)
async def get_data_ingestion(
    data_id: str,
    current_user: User = Depends(get_current_user),
    data_ingestion_usecase: DataIngestionUseCase = Depends(get_data_ingestion_usecase)
):
    """
    Get data ingestion by ID.
    
    - **data_id**: Data ingestion ID
    """
    try:
        data_ingestion = await data_ingestion_usecase.get_data_ingestion(data_id, user=current_user)
        
        return data_ingestion
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
    current_user: User = Depends(get_current_user),
    data_ingestion_usecase: DataIngestionUseCase = Depends(get_data_ingestion_usecase)
):
    """
    Search data ingestion using text query.
    
    - **query**: Search query text (optional)
    - **page**: Page number (default: 1)
    - **page_size**: Number of items per page (default: 10)
    """
    try:
        # Get total count for pagination
        total_count = await data_ingestion_usecase.count_data_ingestion(search_request.query, user=current_user)
        
        # Calculate pagination values
        total_pages = (total_count + search_request.page_size - 1) // search_request.page_size
        skip = (search_request.page - 1) * search_request.page_size
        
        # Get search results with pagination
        search_results = await data_ingestion_usecase.search_data_ingestion(
            query=search_request.query,
            skip=skip,
            limit=search_request.page_size,
            user=current_user
        )
        
        # Format results
        result_items = []
        for result in search_results:
            # Create DataIngestion object from search result
            data_ingestion = DataIngestion(
                id=result["id"],
                title=result["title"],
                specified_text=result["specified_text"],
                data_type=result["data_type"],
                content=result.get("content"),
                reference=result["reference"],
                keywords=result["keywords"],
                file_url=result.get("file_url"),
                file_name=result.get("file_name"),
                webpage_url=result.get("webpage_url"),
                user_id=result.get("user_id"),
                created_at=result["created_at"],
                updated_at=result["updated_at"]
            )
            
            # Add similarity score as an attribute if available
            if "similarity_score" in result:
                setattr(data_ingestion, "similarity_score", result["similarity_score"])
                
            result_items.append(data_ingestion)
        
        # Return standardized response format
        return SearchResponse(
            code=0,
            message="",
            data=result_items,
            page=search_request.page,
            page_size=search_request.page_size,
            total_page=total_pages,
            total_data=total_count,
            data_schema=None
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
    current_user: User = Depends(get_current_user),
    data_ingestion_usecase: DataIngestionUseCase = Depends(get_data_ingestion_usecase)
):
    """
    Delete data ingestion and associated resources.
    
    - **data_id**: Data ingestion ID
    """
    try:
        deleted = await data_ingestion_usecase.delete_data_ingestion(data_id, user=current_user)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Data ingestion not found")
        
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting data ingestion: {str(e)}")


@router.get(
    "/",
    response_model=SearchResponse,
    summary="List all data ingestion with pagination"
)
async def list_data_ingestion(
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_user),
    data_ingestion_usecase: DataIngestionUseCase = Depends(get_data_ingestion_usecase)
):
    """
    List all data ingestion with pagination.
    
    - **page**: Page number (default: 1)
    - **page_size**: Number of items per page (default: 10)
    """
    try:
        # Create a search request with empty query for listing all
        search_request = SearchRequest(query="", page=page, page_size=page_size)
        return await search_data_ingestion(search_request, current_user, data_ingestion_usecase)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/insert-sample-data",
    response_model=List[DataIngestion],
    status_code=status.HTTP_201_CREATED,
    summary="Insert sample data for testing"
)
async def insert_sample_data(
    data_ingestion_usecase: DataIngestionUseCase = Depends(get_data_ingestion_usecase)
):
    """
    Insert sample data for testing purposes.
    
    Returns:
        List[DataIngestion]: List of created data ingestion items
    """
    try:
        # Sample data
        sample_data = [
            DataIngestion(
                title="ประมวลกฎหมายแพ่งและพาณิชย์ มาตรา 420",
                specified_text="ผู้ใดจงใจหรือประมาทเลินเล่อ ทำต่อบุคคลอื่นโดยผิดกฎหมายให้เขาเสียหายถึงแก่ชีวิตก็ดี แก่ร่างกายก็ดี อนามัยก็ดี เสรีภาพก็ดี ทรัพย์สินหรือสิทธิอย่างหนึ่งอย่างใดก็ดี ท่านว่าผู้นั้นทำละเมิดจำต้องใช้ค่าสินไหมทดแทนเพื่อการนั้น",
                data_type="ตัวบทกฎหมาย",
                content="มาตรา 420 ผู้ใดจงใจหรือประมาทเลินเล่อ ทำต่อบุคคลอื่นโดยผิดกฎหมายให้เขาเสียหายถึงแก่ชีวิตก็ดี แก่ร่างกายก็ดี อนามัยก็ดี เสรีภาพก็ดี ทรัพย์สินหรือสิทธิอย่างหนึ่งอย่างใดก็ดี ท่านว่าผู้นั้นทำละเมิดจำต้องใช้ค่าสินไหมทดแทนเพื่อการนั้น",
                reference="ประมวลกฎหมายแพ่งและพาณิชย์",
                keywords=["ละเมิด", "ค่าสินไหมทดแทน", "จงใจ", "ประมาทเลินเล่อ"],
                webpage_url="https://www.samuiforsale.com/law-texts/thailand-civil-code-part-1.html#420"
            ),
            DataIngestion(
                title="การฟ้องคดีละเมิด",
                specified_text="การฟ้องคดีละเมิดต้องฟ้องภายในอายุความ 1 ปี นับแต่วันที่ผู้เสียหายรู้ถึงการละเมิดและรู้ตัวผู้จะพึงต้องใช้ค่าสินไหมทดแทน หรือภายใน 10 ปี นับแต่วันทำละเมิด",
                data_type="FAQ",
                content="การฟ้องคดีละเมิดมีอายุความ 1 ปี นับแต่วันที่ผู้เสียหายรู้ถึงการละเมิดและรู้ตัวผู้จะพึงต้องใช้ค่าสินไหมทดแทน และไม่เกิน 10 ปี นับแต่วันทำละเมิด ตามประมวลกฎหมายแพ่งและพาณิชย์ มาตรา 448",
                reference="ประมวลกฎหมายแพ่งและพาณิชย์ มาตรา 448",
                keywords=["ละเมิด", "อายุความ", "ฟ้องคดี"],
                webpage_url="https://www.samuiforsale.com/law-texts/thailand-civil-code-part-1.html#448"
            ),
            DataIngestion(
                title="Snow White and the Seven Dwarfs",
                specified_text="Mirror, mirror on the wall, who is the fairest of them all?",
                data_type="FICTION",
                content="Snow White and the Seven Dwarfs is a classic fairy tale about a young princess named Snow White who is forced to flee into the forest after her jealous stepmother, the Evil Queen, orders her execution. She finds refuge with seven dwarfs, but the Queen tricks her into eating a poisoned apple. Snow White falls into a deep sleep and is eventually awakened by a prince's kiss.",
                reference="The Brothers Grimm, 1812",
                keywords=["fairy tale", "princess", "magic mirror", "dwarfs", "poisoned apple"],
                webpage_url="https://www.gutenberg.org/files/2591/2591-h/2591-h.htm"
            )
        ]
        
        # Create data ingestion items
        created_items = []
        for item in sample_data:
            data_ingestion = await data_ingestion_usecase.submit_data_ingestion(
                data_ingestion=item
            )
            created_items.append(data_ingestion)
        
        return created_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 