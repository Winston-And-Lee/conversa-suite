from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.fastapi.routes import health_routes, user_routes, chatbot_routes


def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="ConverSA Suite API",
        description="API for ConverSA Suite",
        version="0.1.0",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    app.include_router(health_routes.router, prefix="/api/health", tags=["Health"])
    app.include_router(user_routes.router, prefix="/api/users", tags=["Users"])
    app.include_router(chatbot_routes.router)

    return app 