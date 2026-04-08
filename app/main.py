import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import get_settings
from app.auth import verify_api_key
from app.cache import get_cached, set_cache, close_redis
from app.ai import process_prompt

settings = get_settings()
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    yield
    # shutdown
    await close_redis()
    print("Redis connection closed")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ── Middleware ──────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Prometheus metrics ──────────────────────────────────────
Instrumentator().instrument(app).expose(app)


# ── Schemas ─────────────────────────────────────────────────
class PromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)

class PromptResponse(BaseModel):
    response: str
    model: str
    latency_ms: int
    cache_hit: bool
    request_id: str


# ── Routes ──────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "timestamp": int(time.time())
    }


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.post(
    "/generate-response",
    response_model=PromptResponse,
    dependencies=[Depends(verify_api_key)]
)
@limiter.limit(settings.RATE_LIMIT)
async def generate_response(
    request: Request,
    body: PromptRequest
):
    import uuid
    request_id = str(uuid.uuid4())[:8]

    # 1. check cache
    cached = await get_cached(body.prompt)
    if cached:
        return PromptResponse(
            **cached,
            cache_hit=True,
            request_id=request_id
        )

    # 2. run AI inference
    result = await process_prompt(body.prompt)

    # 3. store in cache
    await set_cache(body.prompt, result)

    return PromptResponse(
        response=result["response"],
        model=result["model"],
        latency_ms=result["latency_ms"],
        cache_hit=False,
        request_id=request_id
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "type": type(exc).__name__}
    )