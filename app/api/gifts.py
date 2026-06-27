from fastapi import APIRouter, HTTPException, Query
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models.schemas import GiftRequest, GiftResponse
from app.services.ai_picker import generate_gifts
from app.services.cache import get_cached, set_cached

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/api/gifts", response_model=GiftResponse)
@limiter.limit("20/minute")
async def get_gifts(
    request,
    body: GiftRequest,
    force_refresh: bool = Query(default=False),
) -> GiftResponse:
    if not force_refresh:
        cached = await get_cached(body)
        if cached:
            cached.cached = True
            return cached

    try:
        result = await generate_gifts(body)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI generation failed: {exc}") from exc

    await set_cached(body, result)
    return result
