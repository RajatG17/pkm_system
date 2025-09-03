import os
import asyncio
import httpx

OLLAMA = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDING_MODEL", "nomic-embed-text")

async def _wait_for_ollama(timeout = 60):
    deadline = asyncio.get_event_loop().time() + timeout
    async with httpx.AsyncClient(timeout=10) as client:
        while True:
            try:
                r = await client.get(f"{OLLAMA}/api/tags")
                if r.status_code == 200:
                    return
            except Exception:
                pass
            if asyncio.get_event_loop().time() > deadline:
                raise RuntimeError(f"Ollama not ready at {OLLAMA}")
            await asyncio.sleep(1)

async def _model_is_present():
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(f"{OLLAMA}/api/tags")
        r.raise_for_status()
        models = r.json().get("models", []) or []
        names= {m.get("name") or m.get("model") for m in models if m}
        return EMBEDDING_MODEL in names
    
async def _pull_model(stream = False):
    async with httpx.AsyncClient(timeout=None) as client:
        r = await client.post(f"{OLLAMA}/api/pull",
                              json={"name": EMBEDDING_MODEL, "stream": stream})
        r.raise_for_status()

async def ensure_model_present():
    await _wait_for_ollama()
    if not await _model_is_present():
        await _pull_model(stream=False)