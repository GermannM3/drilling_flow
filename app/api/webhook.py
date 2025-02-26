"""
Telegram webhook handler for processing incoming updates and managing webhook information.
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, Request, Response, HTTPException
from aiogram import types, exceptions
from app.core.bot import dp, bot

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter()

async def process_telegram_update(data: Dict[Any, Any]) -> None:
    """
    Process incoming Telegram update data.
    
    Args:
        data: Dictionary containing Telegram update data
        
    Raises:
        exceptions.TelegramAPIError: If Telegram API returns an error
        ValueError: If update data is invalid
    """
    try:
        update = types.Update(**data)
        await dp.feed_update(bot=bot, update=update)
    except (ValueError, TypeError) as e:
        logger.error(f"Invalid update data: {e}")
        raise HTTPException(status_code=400, detail="Invalid update format")
    except exceptions.TelegramAPIError as e:
        logger.error(f"Telegram API Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def webhook_handler(request: Request) -> Response:
    """
    Handle incoming webhook updates from Telegram.
    
    Args:
        request: FastAPI request object containing update data
        
    Returns:
        Response: HTTP response indicating success or failure
        
    Raises:
        HTTPException: If update processing fails
    """
    try:
        data = await request.json()
        logger.info("Received webhook update")
        
        await process_telegram_update(data)
        return Response(content="OK", status_code=200)
        
    except Exception as e:
        logger.error(f"Webhook Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/webhook")
async def webhook_info() -> Dict[str, Any]:
    """
    Get current webhook configuration information.
    
    Returns:
        Dict containing webhook status information
        
    Raises:
        HTTPException: If webhook information cannot be retrieved
    """
    try:
        webhook = await bot.get_webhook_info()
        logger.info("Retrieved webhook info successfully")
        
        return {
            "url": webhook.url,
            "has_custom_certificate": webhook.has_custom_certificate,
            "pending_update_count": webhook.pending_update_count,
            "last_error_date": webhook.last_error_date,
            "last_error_message": webhook.last_error_message
        }
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve webhook information"
        ) 