from fastapi import APIRouter
from .health_routes import router as health_router
from .user_routes import router as user_router
from .chatbot_routes import router as chatbot_router
from .assistant_routes import router as assistant_router
from .assistant_ui_routes import router as assistant_ui_router
from .data_ingestion_routes import router as data_ingestion_router
from .file_routes import router as file_router

# Create a combined router
router = APIRouter()

# Include all routes
router.include_router(health_router, prefix="/health", tags=["Health"])
router.include_router(user_router, prefix="/users", tags=["Users"])
router.include_router(chatbot_router)
router.include_router(assistant_router, prefix="/assistant", tags=["Assistant"])
router.include_router(assistant_ui_router, prefix="/assistant-ui", tags=["Assistant UI"])
router.include_router(data_ingestion_router)  # Data ingestion routes already have prefix
router.include_router(file_router, prefix="/files", tags=["Files"])
