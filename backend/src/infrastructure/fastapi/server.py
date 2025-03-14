import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import get_settings
from src.infrastructure.database.mongodb import MongoDB
from src.infrastructure.ai.tracing import setup_langchain_tracing
from src.infrastructure.fastapi.routes import health_routes, user_routes, chatbot_routes, assistant_routes, assistant_ui_routes, data_ingestion_routes, file_routes

logger = logging.getLogger(__name__)
settings = get_settings()

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

def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="Conversa Suite API",
        description="API for Conversa Suite",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # CORS middleware with comprehensive configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        max_age=600,  # Cache preflight requests for 10 minutes
    )
    
    # Add middleware to handle security headers
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        
        # Skip adding security headers for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return response
            
        # Allow unsafe-eval for development if needed
        # In production, you should remove unsafe-eval
        response.headers["Content-Security-Policy"] = "default-src 'self'; connect-src 'self' *; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        # Set more permissive referrer policy
        response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
        # Other security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    # Register routes
    app.include_router(health_routes.router, prefix="/api/health", tags=["Health"])
    app.include_router(user_routes.router, prefix="/api/users", tags=["Users"])
    app.include_router(chatbot_routes.router)
    app.include_router(assistant_routes.router, prefix="/api/assistant", tags=["Assistant"])
    app.include_router(assistant_ui_routes.router, prefix="/api/assistant-ui", tags=["Assistant UI"])
    app.include_router(data_ingestion_routes.router)  # Data ingestion routes already have prefix
    app.include_router(file_routes.router, prefix="/api/files", tags=["Files"])

    # Add root and debug endpoints
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

    return app 