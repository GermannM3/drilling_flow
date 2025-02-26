"""
Bot handlers initialization
"""
from aiogram import Router
from .commands import router as commands_router
from .profile import router as profile_router
from .orders import router as orders_router

# Create main router
router = Router(name="main")

# Include all routers
router.include_router(commands_router)
router.include_router(profile_router)
router.include_router(orders_router)

__all__ = ["router"] 