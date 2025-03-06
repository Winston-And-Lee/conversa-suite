from fastapi import APIRouter

from src.infrastructure.fastapi.routes import user_routes, chatbot_routes

router = APIRouter()

# Include user routes
router.include_router(user_routes.router, prefix="/users", tags=["users"])

# Include chatbot routes
router.include_router(chatbot_routes.router, tags=["chatbot"]) 