# Data Ingestion Scripts

This directory contains scripts for testing and managing data ingestion in the Conversa Suite application.

## File URL and Webpage URL Handling

The application supports ingesting data from file URLs and webpage URLs. The following components are involved in this process:

### DataIngestionUseCase

The `DataIngestionUseCase` class in `src/usecase/data_ingestion/data_ingestion_usecase.py` handles the data ingestion process. It accepts both `file_url` and `webpage_url` parameters in the `submit_data_ingestion` method and includes logic to:

1. Store the URL in the `DataIngestion` model
2. Extract file name and type from file URLs
3. Include the URL in Pinecone metadata
4. Process the content using the appropriate method in the `PineconeRepository` class

### PineconeRepository

The `PineconeRepository` class in `src/interface/repository/pinecone/pinecone_repository.py` includes methods for handling different types of content:

#### File URL Handling

The `load_file_from_url` method:
1. Downloads the file from the URL to a temporary location
2. Determines the file type and loads the document using the appropriate loader
3. Splits the document into chunks
4. Stores each chunk in Pinecone with metadata including the `file_url`

#### Webpage URL Handling

The `load_webpage` method:
1. Loads the webpage content using `WebBaseLoader` from LangChain
2. Extracts the webpage title if available
3. Splits the content into chunks
4. Stores each chunk in Pinecone with metadata including the `webpage_url`

The `upsert_vector` method has been enhanced to:
1. Detect if a `webpage_url` is provided in the metadata
2. Automatically load and process the webpage content
3. Store the content in Pinecone with appropriate metadata

### DataIngestion Model

The `DataIngestion` model in `src/domain/models/data_ingestion.py` includes fields for storing both file and webpage information:

- `file_url`: URL of the file
- `file_name`: Original filename
- `file_type`: File type (PDF, DOC, etc.)
- `file_size`: File size in bytes
- `webpage_url`: URL of the webpage

## Test Scripts

The following scripts are available for testing data ingestion:

- `test_file_url_ingestion.py`: Tests file URL handling functionality
- `test_webpage_loader.py`: Tests webpage loading functionality
- `test_file_loader.py`: Tests file loading functionality
- `test_pinecone_connection.py`: Tests Pinecone connection and functionality
- `test_data_ingestion_with_webpage.py`: Tests the complete data ingestion process with a webpage URL
- `insert_sample_data.py`: Inserts sample data using the API
- `data_ingestion_script.py`: Directly inserts data using the repository

## Usage

### Testing File URL Handling

```bash
python test_file_url_ingestion.py
```

This script will download a test PDF file from a URL, extract metadata, and simulate the data ingestion process.

### Testing Webpage Loading

```bash
python test_webpage_loader.py
```

This script will load content from test web pages, extract metadata, and simulate the data ingestion process.

### Testing Complete Data Ingestion with Webpage URL

```bash
python test_data_ingestion_with_webpage.py
```

This script tests the entire data ingestion flow with a webpage URL, including:
1. Creating a mock user
2. Submitting a webpage URL for ingestion
3. Verifying storage in MongoDB
4. Searching for the content in Pinecone
5. Validating the search results

## Supported Content Types

### File Types

The following file types are supported:

- PDF (`.pdf`)
- Word Documents (`.docx`, `.doc`)
- Text Files (`.txt`)

### Webpage Types

Any webpage that can be loaded by the `WebBaseLoader` from LangChain is supported. This includes:

- HTML pages
- Articles
- Documentation
- Blog posts

## Implementation Details

### File URL Processing

When a file URL is provided to the `submit_data_ingestion` method:

1. The URL is stored in the `DataIngestion` model
2. The file name and type are extracted from the URL
3. The file URL is included in the metadata sent to Pinecone
4. The file is downloaded and processed using the `load_file_from_url` method
5. The file content is chunked and stored in Pinecone
6. The file URL is included in search results

### Webpage URL Processing

When a webpage URL is provided to the `submit_data_ingestion` method:

1. The URL is stored in the `DataIngestion` model
2. The URL is included in the metadata sent to Pinecone
3. The webpage content is loaded using the `load_webpage` method
4. The content is chunked and stored in Pinecone
5. The webpage URL is included in search results

This allows users to search for and retrieve content from both files and webpages based on their content, even if the original content is stored externally. 