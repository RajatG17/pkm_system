from fastapi import APIRouter, Query, HTTPException
from ..db import SessionLocal, Document, Chunk


router = APIRouter()

@router.get("")
def get_context(id:int = Query(..., description="Embedding ID of center chunk"), radius: int = Query(1, ge=0, le=3)):
    """
    Get context chunks around a given chunk identified by its embedding ID."""
    db = SessionLocal()
    try: 
        center = db.query(Chunk).filter(Chunk.embedding_id == id).first()
        if not center:
            raise HTTPException(status_code=404, detail=f"Chunk with embedding ID {id} not found")
        
        all_chunks = db.query(Chunk).filter(Chunk.document_id == center.document_id).order_by(Chunk.position).all()
        pos = center.position
        start = max(0, pos - radius)
        end = min(len(all_chunks), pos+radius+1)
        window = all_chunks[start:end]

        doc = db.query(Document).filter(Document.id == center.document_id).first()

        context_items = [
            {
                "id": c.embedding_id,
                "position": c.position,
                "text": c.text.strip()
            }
            for c in window
        ]
    
        return {
            "ok": True, 
            "center": id, 
            "doc_path": doc.path if doc else "unknown",
            "position": pos, 
            "context": context_items
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[DB ERROR] Failed to get context for chunk with embedding ID {id}: {e}")
        raise HTTPException(status_code=500, detail="Internal error retrieving context")
    finally:
        db.close()
