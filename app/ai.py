import time
import asyncio
import hashlib
from app.config import get_settings

settings = get_settings()

async def process_prompt(prompt: str) -> dict:
    start = time.time()

    if settings.AI_MODEL == "mock":
        result = await _mock_inference(prompt)

    elif settings.AI_MODEL == "openai":
        result = await _openai_inference(prompt)

    else:
        result = await _mock_inference(prompt)

    latency_ms = round((time.time() - start) * 1000)
    return {
        "response": result,
        "model": settings.AI_MODEL,
        "latency_ms": latency_ms
    }


async def _mock_inference(prompt: str) -> str:
    await asyncio.sleep(0.05)  # simulate compute
    fingerprint = hashlib.md5(prompt.encode()).hexdigest()[:8]
    return (
        f"[Mock AI] Processed prompt (id:{fingerprint}) — "
        f"{len(prompt.split())} tokens ingested, "
        f"response generated successfully."
    )


async def _openai_inference(prompt: str) -> str:
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 200
                }
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[OpenAI Error] {str(e)}"