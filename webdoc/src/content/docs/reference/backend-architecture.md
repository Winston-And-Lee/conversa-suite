---
title: Backend Architecture
description: Overview of the backend architecture and repository pattern
---

# Backend Architecture

The ConverSA Suite backend follows a clean architecture pattern with a clear separation of concerns. The system is organized into several layers:

## Domain Layer

The domain layer contains business entities and value objects. It represents the core business models independent of any frameworks or external dependencies.

```
src/domain/
├── models/       # Core domain models (e.g., DataIngestion, User)
└── entity/       # Entity schemas for API requests/responses
```

## Interface Layer

The interface layer defines contracts (interfaces) and implements adapters to external systems.

```
src/interface/
└── repository/   # Repository interfaces and implementations
    ├── mongodb/  # MongoDB implementations
    ├── s3/       # S3 storage implementations
    ├── pinecone/ # Pinecone vector database implementations
    └── database/ # Database connection and factory functions
```

## Use Case Layer

The use cases (or application services) orchestrate the flow of data and implement business rules.

```
src/usecase/
├── data_ingestion/ # Data ingestion use cases
└── user/           # User management use cases
```

## Infrastructure Layer

The infrastructure layer provides implementations for interfaces defined in the interface layer.

```
src/infrastructure/
├── fastapi/        # FastAPI framework implementation
├── services/       # External services 
└── database/       # Database connection implementations
```

## Repository Pattern

The backend implements the repository pattern to abstract data access logic. Each type of data source has its own repository implementation:

### MongoDB Repositories

Repositories that interact with MongoDB collections:
- `DataIngestionRepository`: Manages data ingestion records
- `UserRepository`: Manages user accounts
- `UserVerificationRepository`: Manages user verification codes

### S3 Repository

The `S3Repository` handles file storage operations:
- `upload_file()`: Uploads files to S3 and returns file metadata
- `delete_file()`: Deletes files from S3

### Pinecone Repository

The `PineconeRepository` handles vector database operations:
- `generate_embeddings()`: Generates embeddings using OpenAI
- `upsert_vector()`: Stores vectors in Pinecone
- `semantic_search()`: Performs semantic search queries
- `generate_keywords()`: Generates keywords from text using AI

## Factory Pattern

Repository instances are created through factory functions in `db_repository.py`:

```python
# Get repositories through factory functions
self.data_ingestion_repository = data_ingestion_repository()
self.s3_repository = s3_repository()
self.pinecone_repository = pinecone_repository()
```

This pattern centralizes the creation of repositories and makes it easier to swap implementations or mock repositories for testing.

## Data Flow

1. API requests are handled by FastAPI controllers
2. Controllers call the appropriate use case
3. Use cases orchestrate the interaction between repositories
4. Repositories handle data access and persistence
5. Results flow back through the use case to the controller
6. Controllers transform data into API responses

This architecture ensures:
- Loose coupling between components
- Testability of business logic
- Clear separation of responsibilities
- Consistent error handling
- Flexibility to change infrastructure components 