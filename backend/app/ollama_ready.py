import os
import asyncio
import httpx

OLLAMA = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
GEN_MODEL = os.getenv("GEN_MODEL", "llama3.1:8b")

async def _wait_for_ollama(timeout = 60):
    print(f"[startup] Waiting for Ollama at {OLLAMA}...")
    for i in range(timeout):
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{OLLAMA}/api/tags", timeout=5)
                if r.status_code == 200:
                    print(f"[startup] Ollama is up")
                    return
        except Exception:
            pass
        await asyncio.sleep(1)
    raise RuntimeError(f"Ollama not ready at {OLLAMA} after {timeout} seconds")


async def _model_is_present():
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(f"{OLLAMA}/api/tags")
        r.raise_for_status()
        models = r.json().get("models", []) or []
        names= {m.get("name") or m.get("model") for m in models if m}
        print(names)
        return EMBEDDING_MODEL in names and GEN_MODEL in names
    
async def _pull_model(model, stream = False):
    async with httpx.AsyncClient(timeout=None) as client:
        r = await client.post(f"{OLLAMA}/api/pull",
                              json={"name": model, "stream": stream})
        r.raise_for_status()

async def ensure_model_present():
    await _wait_for_ollama()
    if not await _model_is_present():
        await _pull_model(EMBEDDING_MODEL, stream=False)
        await _pull_model(GEN_MODEL, stream=False)