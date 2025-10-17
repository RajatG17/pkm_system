from __future__ import annotations
from fastapi import APIRouter
from .upload import UPLOAD_DIR
from ..chunking import chunk_text
from ..embeddings import embed_batch
from ..indexer import (create_or_load_index, save_index, load_meta, save_meta,
    load_docmap, save_docmap, sha256_text, sha256_bytes,
    next_ids, remove_ids, l2_normalize
)
from ..extract import extract_text
import faiss
import os, time, glob, numpy as np
from app.db import SessionLocal, Document, Chunk

router = APIRouter()

def upsert_document(path, hash, chunks):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter_by(path=path).first()
        if not doc:
            doc = Document(path=path, hash=hash, type=path.split(".")[-1])
            db.add(doc)
            db.flush()
        else:
            db.query(Chunk).filter_by(document_id=doc.id).delete()
            doc.hash = hash
        
        for pos, chunk_text in enumerate(chunks):
            db.add(Chunk(document_id=doc.id, position=pos, text=chunk_text))
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[DB ERROR] Failed upert for {path}: {e}")
    finally:
        db.close()

def _doc_hash_from_path(path: str):
    try:
        text = extract_text(path)
        return sha256_text(text)
    except Exception:
        with open(path, "rb") as f:
            return sha256_bytes(f.read())
        
@router.post("/reindex")
async def full_reindex():
    """
    fully reindex if needed
    """
    for p in ("data/index.faiss", "data/chunks.json", "data/doc_index.json", "data/id_counter.json"):
        if os.path.exists(p): os.remove(p)
    return await incremental_index()

@router.post("/incremental")
async def incremental_index():
    """
    Incremental indexing:
        - add/replace chunks for new/changed docs
        - remove chunks for deleted pics
    """
    started = time.time()
    files = sorted(glob.glob(os.path.join(UPLOAD_DIR, "*")))

    meta = load_meta()
    docmap = load_docmap()

    to_delete_doc_paths = [dp for dp in docmap.keys() if dp not in files]
    remove_ids_total = 0

    index = None
    index_dim = None
    if os.path.exists("data/index.faiss"):
        index = create_or_load_index()
    
    for dp in to_delete_doc_paths:
        ids = docmap.get(dp, {}).get("chunk_ids", [])
        if index is None and ids:
            index = create_or_load_index()
        removed = remove_ids(index, ids) if index is not None else 0
        remove_ids_total += int(removed)

        for cid in ids:
            meta.pop(str(cid), None)
        docmap.pop(dp, None)

    to_add_previews = 0
    add_ids = []
    add_vecs = []
    new_meta_items = {}

    for path in files:
        new_doc_hash = _doc_hash_from_path(path)
        existing = docmap.get(path)

        if existing and existing.get("doc_hash") == new_doc_hash:
            continue
        
        if existing:
            old_ids = existing.get("chunk_ids", [])
            if old_ids:
                if index is None:
                    index = create_or_load_index()
                remove_ids(index, old_ids)
                for cid in old_ids:
                    meta.pop(str(cid), None)
        
        try:
            text = extract_text(path)
        except Exception:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        
        chunks = chunk_text(text, target_tokens=350, overlap_tokens=50)
        if not chunks:
            docmap[path] = {"doc_hash": new_doc_hash, "chunk_ids":[]}
            continue
        upsert_document(path, new_doc_hash, chunks)
            
        B = 64
        embeddings = []
        for i in range(0, len(chunks), B):
            batch = chunks[i:i+B]
            vecs = await embed_batch(batch)
            embeddings.extend(vecs)
        
        arr = l2_normalize(np.asarray(embeddings, dtype="float32"))
        index_dim = arr.shape[1]
        if index is None:
            index = create_or_load_index(index_dim)
        
        ids = next_ids(len(chunks))

        index.add_with_ids(arr, ids)

        db = SessionLocal()
        try:
 
            doc = db.query(Document).filter_by(path=path).first()
            if doc:
                chunks_db = db.query(Chunk).filter_by(document_id=doc.id).order_by(Chunk.position).all()
                for cid, chunk_db in zip(ids.tolist(), chunks_db):
                    chunk_db.embedding_id = int(cid)
                db.commit()
            db.close()
        except Exception as e:
            print(f"[DB ERROR] Failed to update embedding_ids for {path}: {e}")
        finally:
            db.close()

        cur_ids = ids.tolist()
        for local_pos, (cid, chunk) in enumerate(zip(cur_ids, chunks)):
            new_meta_items[str(int(cid))] = {
                "doc_path": path,
                "position": local_pos,
                "text": chunk,
                "text_preview": chunk.strip().replace("\n\n", "\n")[:500]
            }
        docmap[path] = {"doc_hash": new_doc_hash, "chunk_ids": cur_ids}
        to_add_previews += len(cur_ids)
        add_ids.extend(cur_ids)

    if index is not None:
        save_index(index)
    meta.update(new_meta_items)
    save_meta(meta)
    save_docmap(docmap)

    elapsed = round(time.time() - started, 3)
    return {
        "ok": True,
        "files_seen": len(files), 
        "docs_deleted": len(to_delete_doc_paths),
        "ids_removed": remove_ids_total,
        "new_or_changed_docs": sum(1 for p in files if p in docmap and docmap[p].get("chunk_ids")),
        "chunks_added": len(add_ids),
        "index_dim": index_dim or ("unchanged" if index is not None else None),
        "elapsed_s": elapsed
    }

@router.post("/reset")
async def reset_index():
    removed = []
    for p in ("data/index.faiss", "data/chunks.json", "data/doc_index.json", "data/id_counter.json"):
        if os.path.exists(p):
            os.remove(p)
            removed.append(p)
    return {"reset": removed}

