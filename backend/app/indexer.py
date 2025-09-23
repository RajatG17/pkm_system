### Incremental improvements to indexer
from __future__ import annotations
import os, ujson, json, hashlib
import numpy as np
import faiss
from typing import Dict, List, Tuple

DATA_DIR = "data"
INDEX_PATH = os.path.join(DATA_DIR, "index.faiss")
META_PATH = os.path.join(DATA_DIR, "chunks.json")
DOCMAP_PATH = os.path.join(DATA_DIR, "doc_index.json")
COUNTER_PATH = os.path.join(DATA_DIR, "id_counter.json")

def _ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)

def _read_counter():
    if not os.path.exists(COUNTER_PATH):
        return 0
    with open(COUNTER_PATH, "r") as f: return int(f.read().strip() or "0")

def _write_counter(v):
    with open(COUNTER_PATH, "w") as f: f.write(str(v))

def create_or_load_index(dim: int | None = None):
    """
    Ensure IndexMap2 exists and load it or create a fresh one"""
    _ensure_dirs()

    if os.path.exists(INDEX_PATH):
        idx = faiss.read_index(INDEX_PATH)
        # ensure IDMap2 
        if not isinstance(idx, faiss.IndexIDMap2):
            idx = faiss.IndexIDMap2(idx)
        return idx
    if dim is None:
        raise ValueError("First time index build requires dim")
    base = faiss.IndexFlatIP(dim)
    return faiss.IndexIDMap2(base)


def save_index(index: faiss.Index):
    _ensure_dirs()
    faiss.write_index(index, INDEX_PATH)

def load_meta():
    if not os.path.exists(META_PATH): return {}
    with open(META_PATH, "r", encoding='utf-8') as f:
        return json.load(f)

def save_meta(meta):
    _ensure_dirs()
    with open(META_PATH, "w", encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False)

def load_docmap():
    if not os.path.exists(DOCMAP_PATH):
        return {}
    with open(DOCMAP_PATH, "r", encoding='utf-8') as f:
        return json.load(f)
    
def save_docmap(docmap):
    _ensure_dirs()
    with open(DOCMAP_PATH, "w", encoding='utf-8') as f:
        json.dump(docmap,f, ensure_ascii=False)
    
def sha256_bytes(b: bytes):
    return hashlib.sha256(b).hexdigest()

def sha256_text(s: str):
    return hashlib.sha256(s.encode("utf-8", "ignore")).hexdigest()

def l2_normalize(arr):
    n = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
    return arr/n

def next_ids(n):
    cur = _read_counter()
    ids = np.arange(cur, cur+n, dtype=np.int64)
    _write_counter(int(cur+n))
    return ids

def remove_ids(index: faiss.IndexIDMap2, ids: List[int]):
    if not ids: 
        return 0
    sel = faiss.IDSelectorBatch(np.array(ids, dtype=np.int64))
    return index.remove_ids(sel)

def search(index: faiss.IndexIDMap2, query_vec: np.ndarray, top_k=5):
    q = np.array([query_vec], dtype="float32")
    D, I = index.search(q,top_k)
    return D[0].tolist(), I[0].astype(np.int64).tolist()

    




### Rudimentry Indexer, works

# import faiss, numpy as np, os, ujson, json


# INDEX_PATH = "data/index.faiss"
# META_PATH = "data/chunks.json"

# def _ensure_dirs():
#     os.makedirs("data", exist_ok=True)

# def create_or_load_index(dim):
#     _ensure_dirs()
#     if os.path.exists(INDEX_PATH):
#         return faiss.read_index(INDEX_PATH)

#     index = faiss.IndexFlatIP(dim)
#     return faiss.IndexIDMap2(index)

# def save_index(index):
#     faiss.write_index(index, INDEX_PATH)

# def load_meta():
#     if not os.path.exists(META_PATH):
#         return {}
#     with open(META_PATH, "r", encoding='utf-8') as f:
#         return json.load(f)

# def save_meta(meta_dict):
#     with open(META_PATH, "w", encoding='utf-8') as f:
#         json.dump(meta_dict, f, ensure_ascii=False)

# def next_id_start(meta_dict):
#     return (max(map(int, meta_dict.keys())) + 1) if meta_dict else 0

# def search(index, query_vec, top_k=10):
#     q = np.array([query_vec], dtype="float32")
#     D, I = index.search(q, top_k)
    
#     return D[0].tolist(), I[0].astype(np.int64).tolist()


