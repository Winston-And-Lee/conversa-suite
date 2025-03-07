import io
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import UploadFile
from fastapi.testclient import TestClient

from src.domain.models.data_ingestion import DataIngestion, DataType
from src.domain.entity.data_ingestion import DataTypeEnum
from src.usecase.data_ingestion import DataIngestionUseCase
from main import app


client = TestClient(app)


@pytest.fixture
def mock_data_ingestion_usecase():
    """Fixture for mocking DataIngestionUseCase."""
    mock_usecase = AsyncMock(spec=DataIngestionUseCase)
    
    # Mock methods
    mock_usecase.submit_data_ingestion = AsyncMock()
    mock_usecase.get_data_ingestion = AsyncMock()
    mock_usecase.search_data_ingestion = AsyncMock()
    mock_usecase.delete_data_ingestion = AsyncMock()
    
    return mock_usecase


@pytest.fixture
def sample_data_ingestion():
    """Fixture for sample data ingestion."""
    return DataIngestion(
        id="test_id",
        title="Test Title",
        specified_text="Sample specified text",
        data_type=DataType.LEGAL_TEXT,
        law="Sample Law",
        reference="Sample Reference",
        keywords=["keyword1", "keyword2"],
        file_url="https://example.com/file.pdf",
        file_name="file.pdf",
        file_type="application/pdf",
        file_size=1024,
        pinecone_id="pinecone_id"
    )


@pytest.mark.asyncio
@patch("src.infrastructure.fastapi.routes.data_ingestion_routes.get_data_ingestion_usecase")
async def test_submit_data_ingestion(mock_get_usecase, mock_data_ingestion_usecase, sample_data_ingestion):
    """Test submitting data ingestion."""
    # Set up mock
    mock_get_usecase.return_value = mock_data_ingestion_usecase
    mock_data_ingestion_usecase.submit_data_ingestion.return_value = sample_data_ingestion
    
    # Create a file
    test_file_content = b"test file content"
    test_file = UploadFile(
        filename="test.pdf",
        file=io.BytesIO(test_file_content),
        content_type="application/pdf"
    )
    
    # Prepare form data
    form_data = {
        "title": "Test Title",
        "specified_text": "Sample specified text",
        "data_type": DataTypeEnum.LEGAL_TEXT,
        "law": "Sample Law",
        "reference": "Sample Reference",
        "keywords": ["keyword1", "keyword2"]
    }
    
    # Test the API endpoint with multipart form
    files = {"file": ("test.pdf", test_file_content, "application/pdf")}
    response = client.post("/api/data-ingestion/", data=form_data, files=files)
    
    # Assertions
    assert response.status_code == 201
    result = response.json()
    assert result["title"] == "Test Title"
    assert result["specified_text"] == "Sample specified text"
    assert result["data_type"] == DataType.LEGAL_TEXT.value
    assert "id" in result
    assert "file_url" in result
    
    # Verify usecase was called with correct parameters
    mock_data_ingestion_usecase.submit_data_ingestion.assert_called_once()


@pytest.mark.asyncio
@patch("src.infrastructure.fastapi.routes.data_ingestion_routes.get_data_ingestion_usecase")
async def test_get_data_ingestion(mock_get_usecase, mock_data_ingestion_usecase, sample_data_ingestion):
    """Test getting data ingestion by ID."""
    # Set up mock
    mock_get_usecase.return_value = mock_data_ingestion_usecase
    mock_data_ingestion_usecase.get_data_ingestion.return_value = sample_data_ingestion
    
    # Test the API endpoint
    response = client.get("/api/data-ingestion/test_id")
    
    # Assertions
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == "test_id"
    assert result["title"] == "Test Title"
    assert result["specified_text"] == "Sample specified text"
    assert result["file_url"] == "https://example.com/file.pdf"
    
    # Verify usecase was called with correct parameters
    mock_data_ingestion_usecase.get_data_ingestion.assert_called_once_with("test_id")


@pytest.mark.asyncio
@patch("src.infrastructure.fastapi.routes.data_ingestion_routes.get_data_ingestion_usecase")
async def test_search_data_ingestion(mock_get_usecase, mock_data_ingestion_usecase):
    """Test searching data ingestion."""
    # Set up mock
    mock_get_usecase.return_value = mock_data_ingestion_usecase
    mock_data_ingestion_usecase.search_data_ingestion.return_value = [
        {
            "id": "test_id",
            "title": "Test Title",
            "specified_text": "Sample specified text",
            "data_type": DataType.LEGAL_TEXT.value,
            "similarity_score": 0.95
        }
    ]
    
    # Test the API endpoint
    search_request = {"query": "sample search", "limit": 5}
    response = client.post("/api/data-ingestion/search", json=search_request)
    
    # Assertions
    assert response.status_code == 200
    result = response.json()
    assert "results" in result
    assert len(result["results"]) == 1
    assert result["results"][0]["id"] == "test_id"
    assert result["results"][0]["title"] == "Test Title"
    assert result["results"][0]["similarity_score"] == 0.95
    assert result["total"] == 1
    
    # Verify usecase was called with correct parameters
    mock_data_ingestion_usecase.search_data_ingestion.assert_called_once_with(
        query="sample search", limit=5
    )


@pytest.mark.asyncio
@patch("src.infrastructure.fastapi.routes.data_ingestion_routes.get_data_ingestion_usecase")
async def test_delete_data_ingestion(mock_get_usecase, mock_data_ingestion_usecase):
    """Test deleting data ingestion."""
    # Set up mock
    mock_get_usecase.return_value = mock_data_ingestion_usecase
    mock_data_ingestion_usecase.delete_data_ingestion.return_value = True
    
    # Test the API endpoint
    response = client.delete("/api/data-ingestion/test_id")
    
    # Assertions
    assert response.status_code == 204
    
    # Verify usecase was called with correct parameters
    mock_data_ingestion_usecase.delete_data_ingestion.assert_called_once_with("test_id")


@pytest.mark.asyncio
@patch("src.infrastructure.fastapi.routes.data_ingestion_routes.get_data_ingestion_usecase")
async def test_delete_data_ingestion_not_found(mock_get_usecase, mock_data_ingestion_usecase):
    """Test deleting non-existent data ingestion."""
    # Set up mock
    mock_get_usecase.return_value = mock_data_ingestion_usecase
    mock_data_ingestion_usecase.delete_data_ingestion.return_value = False
    
    # Test the API endpoint
    response = client.delete("/api/data-ingestion/nonexistent_id")
    
    # Assertions
    assert response.status_code == 404
    
    # Verify usecase was called with correct parameters
    mock_data_ingestion_usecase.delete_data_ingestion.assert_called_once_with("nonexistent_id") 