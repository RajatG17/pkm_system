from fastapi import APIRouter, Query

from ..utils.filters import filter_chunks
from ..embeddings import embed_batch
from ..indexer import create_or_load_index, search as faiss_search, load_meta
from ..cache import search_cache
import ujson
import numpy as np
from app.db import get_chunks_by_ids, SessionLocal, Document, Chunk
from datetime import datetime

router = APIRouter()

def l2_normalize(arr):
    n = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
    return arr/n

@router.get("")
async def search(
    q = Query(...), 
    k: int=5,
    file_type: str | None = Query(None, description="Filter by file type"),
    tag: str | None = Query(None, description="Filter by tag"),
    modified_after: str | None = Query(None, description="Filter documents modified after this date"),
):
    """
    Search for relevant chunks given a query string."""
    ## search cache
    ck = (q, k, file_type, tag, modified_after)
    cached = search_cache.get(ck)

    if cached: return cached

    vec = await embed_batch([q])
    arr = l2_normalize(np.array(vec, dtype="float32"))[0]

    # load index
    index= create_or_load_index(arr.shape[0])
    scores, ids = faiss_search(index, arr, top_k=k*3) # retrieve more to filter later

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
    # sanity print
    chunks = filter_chunks(chunks, file_type=file_type, tag=tag, modified_after=modified_after)
    out = sorted(chunks, key=lambda x: -scores[chunks.index(x)])[:k]
    payload = {"query": q, "results": out}
    search_cache.set(ck, payload)

    return payload