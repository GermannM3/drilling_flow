from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

async def setup_cache(app: FastAPI, settings) -> None:
    redis = aioredis.from_url(settings.REDIS_URL)
    FastAPICache.init(RedisBackend(redis), prefix="drillflow-cache")

# Использование в роутерах:
@router.get("/contractors/nearby")
@cache(expire=300)  # Кэш на 5 минут
async def get_nearby_contractors():
    pass 