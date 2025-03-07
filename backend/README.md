# Backend Service

A RESTful API service built with FastAPI and MongoDB, following clean architecture principles.

## Project Structure

```
backend/
├── src/
│   ├── domain/          # Business entities and logic
│   │   ├── entity/      # Business entities
│   │   ├── repository/  # Repository interfaces
│   │   ├── models/      # Data models
│   │   ├── interfaces/  # Domain interfaces
│   │   └── constant/    # Domain constants
│   ├── usecase/         # Application business rules
│   ├── infrastructure/  # External implementations
│   │   ├── database/    # Database implementation
│   │   └── fastapi/     # FastAPI implementation
│   ├── interface/       # Interface adapters
│   ├── config/          # Configuration
│   └── shared/          # Shared utilities
├── test/                # Tests
├── scripts/             # Scripts for deployment, CI/CD
├── deployment/          # Deployment configurations
├── resources/           # Resources, templates, etc.
├── data/                # Data files
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker compose configuration
└── env.template         # Environment variables template
```

## Setup

### Prerequisites

- Python 3.8+
- MongoDB
- AWS S3 account
- Pinecone account
- OpenAI API key

### Environment Variables

Create a `.env` file based on the provided `env.template` with the following settings:

```
# Application settings
APP_NAME=backend-service
APP_ENV=development
DEBUG=true
LOG_LEVEL=debug

# Server settings
HOST=0.0.0.0
PORT=8000

# MongoDB settings
MONGO_URI=mongodb://localhost:27017
MONGO_DB=backend_db
MONGO_USER=
MONGO_PASSWORD=

# JWT settings
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# AWS S3 settings
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_REGION=ap-southeast-1
S3_BUCKET_NAME=your-bucket-name

# Pinecone settings
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=your-pinecone-environment
PINECONE_INDEX_NAME=your-pinecone-index

# OpenAI for embeddings
OPENAI_API_KEY=your-openai-api-key
```

### Installation

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   ```
   # On Windows
   venv\Scripts\activate
   
   # On Unix or MacOS
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Application

Run the application with:

```
python main.py
```

The API will be available at `http://localhost:8000`.

API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Running Tests

Run tests with:

```
pytest
```

## Docker

Build and run the Docker container:

```
docker build -t backend-service .
docker run -p 8000:8000 backend-service
```

## API Usage Examples

### Submit Data

```bash
curl -X 'POST' \
  'http://localhost:8000/api/data-ingestion/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'title=Sample Title' \
  -F 'specified_text=Sample text content' \
  -F 'data_type=ตัวบทกฎหมาย' \
  -F 'law=Sample Law' \
  -F 'reference=Sample Reference' \
  -F 'keywords=keyword1,keyword2' \
  -F 'file=@document.pdf;type=application/pdf'
```

### Search Data

```bash
curl -X 'POST' \
  'http://localhost:8000/api/data-ingestion/search' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "sample search query",
  "limit": 10
}'
```

## License

This project is proprietary and confidential. 