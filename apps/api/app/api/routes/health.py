from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter(prefix="/api/health", tags=["health"])

@router.get("")
def health_check():
    """Basic health check to verify the app is running."""
    return {"status": "healthy"}

@router.get("/ready")
def readiness_check(response: Response, db: Session = Depends(get_db)):
    """Deep health check that verifies database connectivity."""
    try:
        # Execute a simple query
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        response.status_code = 503
        return {"status": "not ready", "error": str(e)}
