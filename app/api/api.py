from fastapi import APIRouter
from app.api.endpoints import chat, images

# Main API router that includes all endpoint routers
api_router = APIRouter()

# Include chat endpoints - handles conversational interactions with AI
api_router.include_router(
    chat.router, 
    prefix="/chat", 
    tags=["chat"]
)

# Include image endpoints - handles image generation and retrieval
api_router.include_router(
    images.router, 
    prefix="/images", 
    tags=["images"]
) 