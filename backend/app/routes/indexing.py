from fastapi import APIRouter
from .upload import UPLOAD_DIR
from ..chunking import chunk_text
from ..embeddings import embed_batch
from ..indexer import create_or_load_index, save_index, save_meta
import faiss
import os, glob, numpy as np

router = APIRouter()

def l2_normalize(arr):
    n = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
    return arr/n

@router.post("/reindex")
async def reindex():
    # primitive plain text doc collection
    files = glob.glob(os.path.join(UPLOAD_DIR, "*"))
    chunks, meta = [], []
    for path in files:
        with open(path, "rb") as f:
            raw = f.read()
        try:
            text = raw.decode('utf-8', errors="ignore")
        except Exception:
            text = raw.decode('latin-1', errors="ignore")
        # TODO: replace later with PDF/MD/code extraction
        parts = chunk_text(text)
        for i, piece in enumerate(parts):
            chunks.append(piece)
            meta.append({'doc_path': path, 'chunk_id': len(meta), 'position': i})
    
    if not chunks:
        return {"indexed_chunks": 0, "dimensions": 0}

    # embed
    vecs = await embed_batch(chunks)
    arr = np.array(vecs, dtype="float32")
    arr = l2_normalize(arr=arr)

    # Index
    dim = arr.shape[1]
    base = faiss.IndexFlatIP(dim)
    index = faiss.IndexIDMap2(base)

    ids = np.arange(len(chunks), dtype=np.int64)
    index.add_with_ids(arr, ids)
    save_index(index)
    meta_dict = {str(i): m for i, m in zip(ids.tolist(), meta)}
    save_meta(meta_dict)

    return {"indexed_chunks": len(chunks), "dimensions": dim}


    
@router.post("/reset")
async def reset_index():
    removed = []
    for p in ("data/index.faiss", "data/chunks.json"):
        if os.path.exists(p):
            os.remove(p)
            removed.append(p)
    
    return {"reset": removed}
    

