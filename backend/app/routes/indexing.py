from fastapi import APIRouter
from .upload import UPLOAD_DIR
from ..chunking import chunk_text
from ..embeddings import embed_batch
from ..indexer import create_or_load_index, save_index, append_metadata
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

    # embed
    vecs = await embed_batch(chunks)
    arr = np.array(vecs, dtype="float32")
    arr = l2_normalize(arr=arr)

    # Index
    dim = arr.shape[1]
    index = create_or_load_index(dim)
    index.add(arr)
    save_index(index)
    append_metadata(meta)

    return {"indexed_chunks": len(chunks), "dimensions": dim}


    

    

