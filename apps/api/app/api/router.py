from fastapi import APIRouter

from app.api.routes import health
from app.api.routes import profiles
from app.api.routes import search
from app.api.routes import chat
from app.api.routes import discovery
from app.api.routes import ingestion

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

# Phase 1 Routes
api_router.include_router(discovery.router, prefix="/search-sessions", tags=["discovery"])
api_router.include_router(ingestion.router, prefix="/search-sessions", tags=["ingestion"])

# Phase 2 Routes
from app.api.routes import retrieval
api_router.include_router(retrieval.router, prefix="/retrieval", tags=["retrieval"])
