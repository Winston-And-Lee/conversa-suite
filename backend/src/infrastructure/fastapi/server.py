from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import os

from src.infrastructure.fastapi.routes import health_routes, user_routes, chatbot_routes, assistant_routes, assistant_ui_routes


def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="ConverSA Suite API",
        description="API for ConverSA Suite",
        version="0.1.0",
    )

    # Get frontend URL from environment or use default
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3001")
    
    # CORS middleware with comprehensive configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[frontend_url, "http://localhost:3001"],  # Allow requests from our frontend
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"],
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

    return app 