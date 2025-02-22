from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from .database import get_db

router = APIRouter()

@router.get("/health")
async def health_check():
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e)) 