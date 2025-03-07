---
title: Data Ingestion Module
description: Understanding the Data Ingestion module architecture and implementation
---

# Data Ingestion Module

The Data Ingestion module is responsible for handling form submissions with file uploads, processing the data, and making it searchable using vector embeddings.

## Architecture Overview

The Data Ingestion module follows the clean architecture pattern with clear separation of concerns:

```
├── domain/
│   ├── models/
│   │   └── data_ingestion.py         # Domain model
│   └── entity/
│       └── data_ingestion/           # API schemas
│           └── data_ingestion_schema.py
├── interface/
│   └── repository/
│       ├── mongodb/
│       │   └── data_ingestion_repository.py
│       ├── s3/
│       │   └── s3_repository.py
│       └── pinecone/
│           └── pinecone_repository.py
└── usecase/
    └── data_ingestion/
        └── data_ingestion_usecase.py
```

## Domain Model

The `DataIngestion` model represents the core business entity with the following properties:

- `id`: Unique identifier
- `title`: Title in Thai (หัวข้อ)
- `specified_text`: Specified text content in Thai (ระบุ)
- `data_type`: Type of data (ตัวบทกฎหมาย, FAQ, คำแนะนำ)
- `law`: Law/regulation reference
- `reference`: Additional reference information
- `keywords`: List of keywords for searchability
- `file_url`: URL to the uploaded file in S3
- `file_name`: Original filename
- `file_type`: MIME type of the file
- `file_size`: Size of the file in bytes
- `pinecone_id`: Vector ID in Pinecone
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Repositories

### Data Ingestion Repository

The `DataIngestionRepository` handles persistence of data ingestion records in MongoDB:

```python
# Create a new data ingestion entry
created_data_ingestion = await self.data_ingestion_repository.create(data_ingestion)

# Get data ingestion by ID
data_ingestion = await self.data_ingestion_repository.get_by_id(data_id)

# Update data ingestion
await self.data_ingestion_repository.update(data_id, {"pinecone_id": pinecone_id})

# Delete data ingestion
deleted = await self.data_ingestion_repository.delete(data_id)
```

### S3 Repository

The `S3Repository` handles file storage in AWS S3:

```python
# Upload file to S3
file_info = await self.s3_repository.upload_file(file)

# Delete file from S3
await self.s3_repository.delete_file(file_url)
```

### Pinecone Repository

The `PineconeRepository` handles vector operations in Pinecone:

```python
# Generate embeddings for text
embedding = await self.pinecone_repository.generate_embeddings(text)

# Store vector in Pinecone
pinecone_id = await self.pinecone_repository.upsert_vector(text_data, metadata)

# Perform semantic search
search_results = await self.pinecone_repository.semantic_search(query, limit)

# Generate keywords from text
keywords = await self.pinecone_repository.generate_keywords(text)

# Delete vector from Pinecone
await self.pinecone_repository.delete_vector(vector_id)
```

## Use Case

The `DataIngestionUseCase` orchestrates the flow of data between repositories:

```python
def __init__(self):
    """Initialize with required repositories and services."""
    # Get repositories through factory functions
    self.data_ingestion_repository = data_ingestion_repository()
    self.s3_repository = s3_repository()
    self.pinecone_repository = pinecone_repository()
    
    # Initialize services
    self.text_extraction_service = TextExtractionService()
    self.logger = logging.getLogger(__name__)
```

Key operations:
- `submit_data_ingestion`: Handles form submission with file upload
- `get_data_ingestion`: Retrieves data by ID
- `search_data_ingestion`: Performs semantic search
- `delete_data_ingestion`: Deletes data and associated resources

## Data Flow

1. **Form Submission**:
   - User submits form with optional file upload
   - FastAPI controller calls the use case
   - File is uploaded to S3 (if provided)
   - Text is extracted from the file
   - Keywords are generated if not provided
   - Data is saved to MongoDB
   - Vector embeddings are created and stored in Pinecone
   - Pinecone ID is updated in MongoDB

2. **Search**:
   - User sends search query
   - Controller calls the use case
   - Text is converted to vector embedding
   - Semantic search is performed in Pinecone
   - Results are returned with similarity scores

3. **Deletion**:
   - Data is retrieved from MongoDB
   - Vector is deleted from Pinecone
   - File is deleted from S3
   - Data is deleted from MongoDB

## API Endpoints

- `POST /api/data-ingestion/`: Submit data with file
- `GET /api/data-ingestion/{data_id}`: Get data by ID
- `POST /api/data-ingestion/search`: Search data
- `DELETE /api/data-ingestion/{data_id}`: Delete data

## Form Fields

- **หัวข้อ (Heading/Title)**: Text input field
- **ระบุ (Specify)**: Text input field
- **ประเภทข้อมูล (Data Type)**:
  - **ตัวบทกฎหมาย** (Legal Text/Article)
  - **FAQ**
  - **คำแนะนำ** (Recommendation/Advice)
- **กฎหมาย (Law/Regulation)**: Select field
- **อ้างอิง (Reference)**: Select field
- **คีย์เวิร์ด (Keywords)**: Automatically generated or manually provided
- **File Upload**: Supports PDF and DOC files, maximum 10MB 