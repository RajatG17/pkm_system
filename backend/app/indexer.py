import faiss, numpy as np, os, ujson

INDEX_PATH = "data/index.faiss"
META_PATH = "data/chunks.jsonl"

def _ensure_dirs():
    os.makedirs("data", exist_ok=True)

def create_or_load_index(dim):
    _ensure_dirs()
    if os.path.exists(INDEX_PATH):
        return faiss.read_index(INDEX_PATH)

    index = faiss.IndexFlatIP(dim)
    return index

def save_index(index):
    faiss.write_index(index, INDEX_PATH)

def append_metadata(items):
    with open(META_PATH, "a", encoding="utf-8") as f:
        for x in items:
            f.write(ujson.dumps(x) + "\n")
    
def search(index, query_vec, top_k=10):
    q = np.array([query_vec], dtype="float32")
    D, I = index.search(q, top_k)
    
    return D[0].tolist(), I[0].tolist()


