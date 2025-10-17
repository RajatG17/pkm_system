from fastapi import FastAPI, Request
from .routes import upload, indexing, search, qa, context
from .ollama_ready import ensure_model_present, EMBEDDING_MODEL, GEN_MODEL
from fastapi.middleware.cors import CORSMiddleware
import logging, os, time
from .metrics import incr, observe, render_prom
from fastapi.responses import PlainTextResponse
from app.db import init_db, DB_PATH


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
    logging.getLogger("uvicorn").info("Ollama text generation model ensures : %s", GEN_MODEL)
    
@app.on_event("startup")
async def verify_db():
    init_db()
    if os.path.exists(DB_PATH):
        logging.getLogger("uvicorn").info(f"DB file exists at {DB_PATH}")
    else:
        logging.getLogger("uvicorn").warning(f"DB file does not exist at {DB_PATH}")
    
@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.middleware("http")
async def metrics_mw(request: Request, call_next):
    t0 = time.perf_counter()
    resp = await call_next(request)
    ms = (time.perf_counter() - t0) * 1000.0
    path = request.url.path or ""
    if path.startswith("/search"):
        observe("search_latency_ms", ms); incr("search_requests_total")
    elif path.startswith("/qa"):
        observe("qa_latency_ms", ms); incr("qa_requests_total")
    elif path.startswith("/index"):
        observe("index_latency_ms", ms); incr("index_requests_total")
    return resp

@app.get("/metrics")    
async def metrics():
    return PlainTextResponse(render_prom(), media_type="text/plain")

app.include_router(upload.router, prefix="/files")
app.include_router(indexing.router, prefix="/index")
app.include_router(search.router, prefix="/search")
app.include_router(qa.router, prefix="/qa")
app.include_router(context.router, prefix="/context")