from fastapi import APIRouter, Query
import numpy as np, os, httpx

from ..embeddings import embed_batch
from ..indexer import create_or_load_index, load_meta, search as faiss_search
from ..prompts import build_qa_prompt
from ..cache import qa_cache

router = APIRouter()

OLLAMA = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
GEN_MODEL = os.getenv("GEN_MODEL", "llama3.1:8b")

def l2_normalize(arr):
    n = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
    return arr / n

@router.get("")
async def qa(q: str = Query(..., description="User question"),
             k: int = 5,
             max_ctx_chars: int = 2400):
    """
    Minimal RAG:
      1) embed question
      2) retrieve top-k chunks
      3) trim context so prompt stays small
      4) call Ollama generate
    """
    ## cache
    ck = (q, k, max_ctx_chars)
    cached = qa_cache.get(ck)
    if cached: return cached
    # 1) Embed query
    vec = await embed_batch([q])
    qv = l2_normalize(np.array(vec, dtype="float32"))[0]

    # 2) Retrieve
    index = create_or_load_index(qv.shape[0])
    scores, ids = faiss_search(index, qv, top_k=k)

    meta = load_meta()
    contexts = []
    total = 0
    for i in ids:
        m = meta.get(str(i))
        if not m: 
            continue
        preview = (m.get("text_preview") or "").strip()
        # Trim per-chunk to keep prompt brisk
        trimmed = preview[:max(100, min(len(preview), max_ctx_chars // max(1, k)))]
        contexts.append({**m, "text_preview": trimmed})
        total += len(trimmed)

    # 3) Build prompt
    prompt = build_qa_prompt(q, contexts)

    # 4) Generate with Ollama
    async with httpx.AsyncClient(timeout=180) as client:
        r = await client.post(f"{OLLAMA}/api/generate", json={
            "model": GEN_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": 4096,
                "temperature": 0.2,
                "top_p": 0.9
            }
        })
        r.raise_for_status()
        answer = r.json().get("response", "").strip()

    payload = {
        "question": q,
        "answer": answer,
        "sources": [
            {
                "id": i,
                "score": float(s),
                "doc_path": meta.get(str(i), {}).get("doc_path"),
                "position": meta.get(str(i), {}).get("position"),
                "preview": meta.get(str(i), {}).get("text_preview", "")[:240]
            }
            for s, i in sorted(zip(scores, ids), key=lambda x: -x[0])
            if meta.get(str(i))
        ]
    }

    qa_cache.set(ck, payload)

    return payload
