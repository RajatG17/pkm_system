import os, httpx
from .ollama_ready import ensure_model_present
from .cache import embed_cache

OLLAMA = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMB_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

async def embed_batch(texts, max_retries = 1):
    key = tuple(texts)
    cached = embed_cache.get(key)
    if cached is not None:
        return cached
    payload = {"model": EMB_MODEL, "input": texts}
    attempt = 0
    async with httpx.AsyncClient(timeout=60) as client:
        while True:
            try:
                r = await client.post(f"{OLLAMA}/api/embed", json=payload)
                r.raise_for_status()
                data = r.json()
                # check structure of data
                print(data)

                if data and "embeddings" in data:
                    res = data["embeddings"] 
                    embed_cache.set(key, res)
                    return res
                
                res = data["embedding"]
                embed_cache.set(key, res)
                return res
            
            except httpx.HTTPStatusError as e:
                if e.response is not None and e.response.status_code == 404 and attempt < max_retries:
                    await ensure_model_present()
                    attempt += 1
                    continue
                raise



