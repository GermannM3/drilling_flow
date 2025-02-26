"""
API endpoints
"""
from fastapi import APIRouter

router = APIRouter()

from .webhook import router as webhook_router
router.include_router(webhook_router, prefix="/webhook", tags=["webhook"]) 