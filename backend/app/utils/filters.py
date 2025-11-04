from ..db import SessionLocal, Document, Chunk
from datetime import datetime

def filter_chunks(chunks, file_type=None, tag=None, modified_after=None):
    """
    Filter chunks using optional critetria: file_type, tag, modified_after.
    """
    if not (file_type or tag or modified_after):
        return chunks
    
    db = SessionLocal()
    filtered = [] 
    
    try:
        doc_paths = {c["doc_path"] for c in chunks}
        docs = {
            d.path: d
            for d in db.query(Document).filter(Document.path.in_(doc_paths)).all()
        }
        for c in chunks:
            doc = docs.get(c["doc_path"])
            if not doc:
                continue

            if file_type and (doc.type or "").lower() != file_type.lower():
                continue
            
            # filter by tags
            if tag and tag.lower() not in (doc.tags or "").lower():
                continue
            
            # filter by modified date
            if modified_after:
                try:
                    dt = datetime.fromisoformat(modified_after)
                    if doc.modified and doc.modified < dt:
                        continue
                except Exception as e:
                    print(f"[WARN] Invalid modified_after param: {e}")
                    pass
            
            filtered.append({
                **c,
                "tags": doc.tags,
                "type": doc.type,
                "modified": str(doc.modified),
            })
        return filtered
    except Exception as e:
        print(f"[FILTER ERROR] {e}")
    finally:
        db.close()