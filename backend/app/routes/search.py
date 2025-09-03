from fastapi import APIRouter, Query
from ..embeddings import embed_batch
from ..indexer import create_or_load_index, search as faiss_search
import ujson
import numpy as np

router = APIRouter()

def l2_normalize(arr):
    n = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
    return arr/n

@router.get("")
async def search(q = Query(...), k: int=5):
    vec=  await embed_batch([q])
    arr = l2_normalize(np.array(vec, dtype="float32"))
    index= create_or_load_index(arr.shape[1])
    scores, ids = faiss_search(index, arr[0], top_k=k)

    # read metadata linearly 
    metas = []
    with open("data/chunks.jsonl", "r", encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i in ids:
                metas.append(ujson.loads(line))
        
    return {"query": q, "results": [
        {"score": float(s), **m} for s, m in sorted(zip(scores, metas), key=lambda x:-x[0])
    ]}