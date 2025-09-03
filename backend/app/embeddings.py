import os, httpx
from .ollama_ready import ensure_model_present

OLLAMA = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMB_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

async def embed_batch(texts, max_retries = 1):
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
                    return data["embeddings"] 
                return data["embedding"]
            
            except httpx.HTTPStatusError as e:
                if e.response is not None and e.response.status_code == 404 and attempt < max_retries:
                    await ensure_model_present()
                    attempt += 1
                    continue
                raise



