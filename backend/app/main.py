from fastapi import FastAPI
from .routes import upload, indexing, search, qa
from .ollama_ready import ensure_model_present
from fastapi.middleware.cors import CORSMiddleware
import logging, os

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def _startup():
    await ensure_model_present()
    logging.getLogger("uvicorn").info("Ollama embedding model ensures : %s", EMBEDDING_MODEL)

@app.get("/health")
async def health_check():
    return {"status": "ok"}


app.include_router(upload.router, prefix="/files")
app.include_router(indexing.router, prefix="/index")
app.include_router(search.router, prefix="/search")
app.include_router(qa.router, prefix="/qa")
