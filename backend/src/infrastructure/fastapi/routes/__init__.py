from fastapi import APIRouter
from .health_routes import router as health_router
from .user_routes import router as user_router
from .chatbot_routes import router as chatbot_router

# Create a combined router
router = APIRouter()

# Include all routes
router.include_router(health_router, prefix="/health", tags=["Health"])
router.include_router(user_router, prefix="/users", tags=["Users"])
router.include_router(chatbot_router)
