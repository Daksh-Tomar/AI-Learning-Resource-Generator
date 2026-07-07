from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.services.retrieval.service import RetrievalService
from app.schemas.retrieval import RerankedCandidate

router = APIRouter()

@router.get("/chunks", response_model=List[RerankedCandidate])
async def search_chunks(
    query: str = Query(..., description="The search query"),
    resource_id: Optional[UUID] = Query(None, description="Optional resource ID to filter by"),
    top_k: int = Query(10, description="Number of results to return"),
    use_reranker: bool = Query(True, description="Whether to use cross-encoder reranking"),
    db: Session = Depends(get_db)
):
    """
    Search across transcript chunks using hybrid retrieval (Dense + Lexical + RRF + Reranker).
    """
    retrieval_service = RetrievalService(db)
    
    try:
        candidates = await retrieval_service.search(
            query=query,
            resource_id_filter=str(resource_id) if resource_id else None,
            top_k=top_k,
            use_reranker=use_reranker
        )
        return candidates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
