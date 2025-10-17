from fastapi import APIRouter, Query
from ..embeddings import embed_batch
from ..indexer import create_or_load_index, search as faiss_search, load_meta
from ..cache import search_cache
import ujson
import numpy as np
from app.db import get_chunks_by_ids


router = APIRouter()

def l2_normalize(arr):
    n = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
    return arr/n

@router.get("")
async def search(q = Query(...), k: int=5):
    """
    Search for relevant chunks given a query string."""
    ## search cache
    ck = (q, k)
    cached = search_cache.get(ck)

    if cached: return cached

    vec = await embed_batch([q])
    arr = l2_normalize(np.array(vec, dtype="float32"))[0]

    # load index
    index= create_or_load_index(arr.shape[0])
    scores, ids = faiss_search(index, arr, top_k=k)

    ## read metadata linearly : replace by DB retrieval using FAISS IDs
    # meta = load_meta()
    # # meta check
    # # print(meta)
    # out = []
    # seen = set()
    # for s,i in sorted(zip(scores, ids), key=lambda x: -x[0]):
    #     m = meta.get(str(i))
    #     if not m:
    #         continue
    #     key = (m["doc_path"], m["position"])
    #     if key in seen:
    #         continue
    #     seen.add(key)
    #     out.append({"score": float(s), "id":int(i), **m})

    chunks = get_chunks_by_ids(ids)
    ## sanity print
    print(chunks[0])
    out = [
        {
            "score": float(s),
            "id": c["embedding_id"],
            **c
        }
        for s, c in sorted(zip(scores, chunks), key=lambda x: -x[0])
        if c.get("embedding_id")
    ]

    payload = {"query": q, "results": out}
    search_cache.set(ck, payload)

    return payload