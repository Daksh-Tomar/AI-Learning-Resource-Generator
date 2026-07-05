from fastapi import APIRouter
from app.api.routes import chat, profiles, search, health

api_router = APIRouter()
api_router.include_router(chat.router)
api_router.include_router(profiles.router)
api_router.include_router(search.router)
api_router.include_router(health.router)
