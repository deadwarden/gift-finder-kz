import hashlib
import json
from typing import Optional

import redis.asyncio as aioredis

from app.config import settings
from app.models.schemas import GiftRequest, GiftResponse

_redis: Optional[aioredis.Redis] = None

CACHE_TTL = 7200  # 2 hours


def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis


def cache_key(req: GiftRequest) -> str:
    payload = req.model_dump_json()
    return "gifts:" + hashlib.md5(payload.encode()).hexdigest()


async def get_cached(req: GiftRequest) -> Optional[GiftResponse]:
    try:
        r = get_redis()
        data = await r.get(cache_key(req))
        if data:
            return GiftResponse.model_validate_json(data)
    except Exception:
        pass
    return None


async def set_cached(req: GiftRequest, resp: GiftResponse) -> None:
    try:
        r = get_redis()
        await r.setex(cache_key(req), CACHE_TTL, resp.model_dump_json())
    except Exception:
        pass
