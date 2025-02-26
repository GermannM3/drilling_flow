"""
API endpoints
"""
from fastapi import APIRouter

router = APIRouter()

# Import and include routers
from .webhook import router as webhook_router
router.include_router(webhook_router, prefix="/webhook", tags=["webhook"]) 