from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.config import get_settings

settings = get_settings()

api_key_header = APIKeyHeader(
    name=settings.API_KEY_NAME,
    auto_error=False
)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header missing"
        )
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    return api_key