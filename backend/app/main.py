from fastapi import FastAPI, Request
from .routes import upload, indexing, search, qa
from .ollama_ready import ensure_model_present
from fastapi.middleware.cors import CORSMiddleware
import logging, os, time
from .metrics import incr, observe, render_prom
from fastapi.responses import PlainTextResponse

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


@app.middleware("http")
async def metrics_mw(request: Request, call_next):
    start = time.time()
    try:
        resp = await call_next(request)
        return resp
    finally:
        ms = (time.perf_counter() - start) * 1000.0
        path = request.url.path
        if path.startswith("/search"): observe("search_latency_ms", ms); incr("search_requests_call")
        if path.startswith("/qa"): observe("qa_latency_ms", ms); incr("qa_requests_total")
        if path.startswith("/index"): observe("index_latency_ms", ms); incr("index_requests_tital")

@app.get("/metrics")    
async def metrics():
    return PlainTextResponse(render_prom(), media_type="text/plain")


app.include_router(upload.router, prefix="/files")
app.include_router(indexing.router, prefix="/index")
app.include_router(search.router, prefix="/search")
app.include_router(qa.router, prefix="/qa")
