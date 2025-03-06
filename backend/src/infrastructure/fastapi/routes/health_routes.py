from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_check():
    """API health check endpoint."""
    return {
        "status": "ok",
        "message": "ConverSA Suite API is running"
    } 