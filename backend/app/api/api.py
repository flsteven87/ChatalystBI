from fastapi import APIRouter
from app.api.endpoints import chat, images

api_router = APIRouter()
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(images.router, prefix="/images", tags=["images"]) 