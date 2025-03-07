"""
Health check routes.
"""
from fastapi import APIRouter, Response

router = APIRouter(tags=["Health"])


@router.get("/")
async def health_check():
    """API health check endpoint."""
    return {
        "status": "ok",
        "message": "ConverSA Suite API is running"
    }


@router.get("/ping")
async def ping():
    """Health check endpoint."""
    return {"status": "ok", "message": "pong"}


@router.options("/cors-test")
@router.get("/cors-test")
async def cors_test():
    """Test endpoint for CORS configuration."""
    return {"status": "ok", "message": "CORS is working!"} 