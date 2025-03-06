import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager
import sys

from src.config.settings import get_settings
from src.infrastructure.database.mongodb import MongoDB
from src.infrastructure.fastapi.routes import router
from src.infrastructure.ai.tracing import setup_langchain_tracing

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Set specific loggers to DEBUG level
for logger_name in ["src.infrastructure.database", "src.interface.repository", "src.usecase"]:
    logging.getLogger(logger_name).setLevel(logging.DEBUG)

settings = get_settings()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI app.
    This handles database connections at startup and shutdown.
    """
    # Startup: Initialize database connection
    try:
        logger.info("Starting up: Connecting to MongoDB...")
        await MongoDB.connect_to_database()
        
        # Force initialize the user_usecase to ensure it has a valid repository
        from src.usecase.user import get_user_usecase_async
        user_usecase = await get_user_usecase_async()
        if user_usecase.user_repository is None:
            logger.error("Failed to initialize user repository during startup")
        else:
            logger.info("Successfully initialized user repository")
            
        logger.info("Database connection established successfully during startup")
        
        # Set up LangChain tracing
        logger.info("Setting up LangChain tracing...")
        setup_langchain_tracing()
    except Exception as e:
        logger.error(f"Failed to initialize database connection during startup: {str(e)}")
        # Don't crash the app, but log the error
    
    yield  # Application runs here
    
    # Shutdown: Close database connection
    try:
        logger.info("Shutting down: Closing MongoDB connection...")
        await MongoDB.close_database_connection()
        logger.info("MongoDB connection closed successfully")
    except Exception as e:
        logger.error(f"Error during database disconnection: {str(e)}")

# Create FastAPI app with lifespan context manager
app = FastAPI(
    title="Conversa Suite API",
    description="API for Conversa Suite",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
logger.info("Registering API routes...")
app.include_router(router, prefix="/api")
logger.info(f"Routes registered: {[route.path for route in app.routes if hasattr(route, 'path')]}")

@app.get("/")
async def root():
    return {"message": "Welcome to Conversa Suite API!"}

@app.get("/debug/routes")
async def debug_routes():
    """Return all registered routes for debugging."""
    routes = []
    for route in app.routes:
        routes.append({
            "path": route.path if hasattr(route, "path") else str(route),
            "name": route.name if hasattr(route, "name") else None,
            "methods": route.methods if hasattr(route, "methods") else None
        })
    return {"routes": routes}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    ) 