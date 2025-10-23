import os
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Float, ForeignKey, DateTime, func
)
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

## DB path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "..", "data")
os.makedirs(DB_DIR, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, "pkm.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, index=True)
    hash = Column(String, index=True)
    modified = Column(DateTime, server_default=func.now(), onupdate=func.now())
    type = Column(String)
    size = Column(Integer, default=0)
    tags = Column(String, default="") 

    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    position = Column(Integer, index=True)
    text = Column(Text)
    embedding_id = Column(Integer, index=True, nullable=True)

    document = relationship("Document", back_populates="chunks")


class Embedding(Base):
    __tablename__ = "embeddings"
    id = Column(Integer, primary_key=True)
    chunk_id = Column(Integer, ForeignKey("chunks.id"), unique=True)
    dim = Column(Integer)
    vector_path = Column(String)

def get_chunks_by_ids(faiss_ids):
    """
    Get chunks from DB by their embedding IDs.
    """
    if not faiss_ids:
        return []
    
    db = SessionLocal()
    try:
        results = (
            db.query(Chunk, Document)
            .join(Document, Chunk.document_id == Document.id)
            .filter(Chunk.embedding_id.in_(faiss_ids))
            .order_by(Chunk.position)
            .all()
        )

        formatted = []
        for chunk, doc in results:
            formatted.append({
                "embedding_id": chunk.embedding_id,
                "chunk_id": chunk.id,
                "position": chunk.position,
                "doc_path": doc.path,
                "text": chunk.text,
                "text_preview": chunk.text.strip().replace("\n\n", "\n")[:500]
            })
        return formatted
    except Exception as e:
        print(f"[DB ERROR] Failed to get chunks for IDs {faiss_ids}: {e}")
        return []
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    