import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.config import get_settings

settings = get_settings()

@pytest.fixture
def api_headers():
    return {"X-API-Key": settings.API_KEY}

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_generate_no_key():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        r = await client.post(
            "/generate-response",
            json={"prompt": "hello"}
        )
    assert r.status_code == 401

@pytest.mark.asyncio
async def test_generate_wrong_key():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        r = await client.post(
            "/generate-response",
            headers={"X-API-Key": "wrong-key"},
            json={"prompt": "hello"}
        )
    assert r.status_code == 403

@pytest.mark.asyncio
async def test_generate_success(api_headers):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        r = await client.post(
            "/generate-response",
            headers=api_headers,
            json={"prompt": "what is devops?"}
        )
    assert r.status_code == 200
    data = r.json()
    assert "response" in data
    assert "latency_ms" in data
    assert "cache_hit" in data

@pytest.mark.asyncio
async def test_empty_prompt(api_headers):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        r = await client.post(
            "/generate-response",
            headers=api_headers,
            json={"prompt": ""}
        )
    assert r.status_code == 422