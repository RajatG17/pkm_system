import faiss, numpy as np, os, ujson, json


INDEX_PATH = "data/index.faiss"
META_PATH = "data/chunks.json"

def _ensure_dirs():
    os.makedirs("data", exist_ok=True)

def create_or_load_index(dim):
    _ensure_dirs()
    if os.path.exists(INDEX_PATH):
        return faiss.read_index(INDEX_PATH)

    index = faiss.IndexFlatIP(dim)
    return faiss.IndexIDMap2(index)

def save_index(index):
    faiss.write_index(index, INDEX_PATH)

def load_meta():
    if not os.path.exists(META_PATH):
        return {}
    with open(META_PATH, "r", encoding='utf-8') as f:
        return json.load(f)

def save_meta(meta_dict):
    with open(META_PATH, "w", encoding='utf-8') as f:
        json.dump(meta_dict, f, ensure_ascii=False)

def next_id_start(meta_dict):
    return (max(map(int, meta_dict.keys())) + 1) if meta_dict else 0

def search(index, query_vec, top_k=10):
    q = np.array([query_vec], dtype="float32")
    D, I = index.search(q, top_k)
    
    return D[0].tolist(), I[0].astype(np.int64).tolist()


