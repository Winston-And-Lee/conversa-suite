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

## Setup and Installation

### Prerequisites

- Python 3.9+
- MongoDB

### Environment Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Copy the environment template:
   ```
   cp env.template .env
   ```
5. Update the environment variables in `.env` as needed

### Running the Application

Start the application:
```
python -m src.infrastructure.fastapi.main
```

Or with uvicorn directly:
```
uvicorn src.infrastructure.fastapi.main:app --reload
```

## Docker Setup

Build and run with Docker Compose:
```
docker-compose up -d
```

## Testing

Run tests:
```
pytest
```

Run tests with coverage:
```
pytest --cov=src tests/
``` 