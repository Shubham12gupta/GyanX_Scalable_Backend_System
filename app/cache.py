import redis.asyncio as redis
import hashlib
import json
from app.config import get_settings

settings = get_settings()

_redis_client = None

async def get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD or None,
            decode_responses=True
        )
    return _redis_client

def make_cache_key(prompt: str) -> str:
    hashed = hashlib.sha256(prompt.strip().lower().encode()).hexdigest()
    return f"response:{hashed}"

async def get_cached(prompt: str) -> dict | None:
    try:
        r = await get_redis()
        key = make_cache_key(prompt)
        data = await r.get(key)
        if data:
            return json.loads(data)
    except Exception:
        pass  # cache miss is fine, never crash on redis failure
    return None

async def set_cache(prompt: str, response: dict):
    try:
        r = await get_redis()
        key = make_cache_key(prompt)
        await r.setex(key, settings.CACHE_TTL, json.dumps(response))
    except Exception:
        pass  # non-critical

async def close_redis():
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None