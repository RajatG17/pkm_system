# Scalable Personal Knowledge Management (PKM) System

#### A privacy-focused, AI-powered platform to **store, search, summarize, and interact** with documents, notes, and code — built on modern **vector search** and **LLMs**.

---

## Overview

This project aims to make personal and team knowledge truly **searchable and intelligent** — using local models and scalable backend infrastructure.

It provides a **self-hosted RAG (Retrieval-Augmented Generation)** system where users can upload files, perform semantic search, and ask questions — all while keeping data private and on-device.

Built modularly, with each phase introducing a core feature, it can scale from a simple local service to a multi-user cloud deployment.

---

## Core Features

| Feature                         | Description                                                                                                      |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **Document Ingestion**    | Upload PDFs, Markdown, text, or code. Extracts and tokenizes automatically for embedding.                        |
| **Semantic Indexing**     | Uses**FAISS** for high-speed vector search with support for **Ollama** embeddings.                   |
| **Semantic Search**       | Natural-language retrieval across all indexed documents.                                                         |
| **Q&A Engine (RAG)**      | Summarization and question-answering powered by**Gemma**, **Llama**, or **GPT-4** (pluggable). |
| **Persistent Storage**    | SQLite + FAISS integration for document, chunk, and embedding metadata.                                          |
| **Incremental Indexing**  | Detects added/changed/deleted files and updates embeddings automatically.                                        |
| **Filters & Tagging**     | Search or QA restricted by file type, tags, or last modified date.                                               |
| **Context Viewer**        | Interactive modal showing contextual chunks around results.                                                      |
| **Evaluation Harness**    | Measures latency, hit@k, and retrieval coverage to assess performance.                                           |
| **Dockerized Deployment** | Backend (FastAPI) + Frontend (React) microservices, CI/CD-ready.                                                 |
| **Apple Silicon Support** | Fully compatible with M-series Macs and ARM containers.                                                          |

---

##  Architecture

```text
                        ┌───────────────────────┐
                        │       Frontend        │
                        │     (React + UI)      │
                        │  • Upload Docs        │
                        │  • Search + QA UI     │
                        │  • Context Viewer     │
                        └─────────┬─────────────┘
                                  │ REST (FastAPI)
                                  ▼
 ┌──────────────────────────────────────────────────────────┐
 │                        Backend                           │
 │──────────────────────────────────────────────────────────│
 │ FastAPI microservices:                                   │
 │  • /upload → document ingestion                          │
 │  • /index → chunk + embedding                            │
 │  • /search → FAISS retrieval + filters                   │
 │  • /qa → LLM-powered Q&A                                 │
 │                                                          │
 │ Components:                                              │
 │  🧠 Embeddings via Ollama (Gemma / Llama)                │
 │  🔍 FAISS Vector Index (local)                           │
 │  💾 SQLite metadata DB (Document, Chunk, Tag)            │
 │  🧰 Cache layer (LRU / Redis-ready)                      │
 │  📈 (TODO) Prometheus metrics for latency + accuracy     │
 └──────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer            | Tools                                   |
| ---------------- | --------------------------------------- |
| Frontend         | React, Tailwind, Axios                  |
| Backend          | FastAPI, httpx, SQLAlchemy              |
| Vector Search    | FAISS                                   |
| LLM / Embeddings | Ollama (Gemma, Llama), GPT-4 (optional) |
| Database         | SQLite (persistent), ready for Postgres |
| Infra & DevOps   | Docker, Docker Compose, GitHub Actions  |
| Monitoring       | Prometheus, Grafana (planned)           |

---

## Current Capabilities

- Upload documents (PDF, .md, .txt, .py, etc.)
- Incremental indexing with document hash tracking
- FAISS + Ollama embeddings for semantic retrieval
- Filter search/QA by:
  - File type (e.g., pdf, md, code)
  - Tag (e.g., AI, research)
  - Modified date (e.g., 2025-01-01)
- Responsive UI with search results and context modal
- Metrics collection for evaluation (hit@k, coverage, latency)

## Example Usage

### Search

```bash
curl "http://localhost:8000/search?q=faiss&file_type=pdf&tag=AI"
```

### Ask a Question

```bash
curl "http://localhost:8000/qa?q=What+is+FAISS+used+for?&tag=AI"
```

### Tag a Document

```bash
curl -X POST "http://localhost:8000/tags?path=uploads/hello.txt&tags=AI,ML"
```

## Setup Instructions

1. Clone the repo

```bash
git clone https://github.com/<your-username>/pkm-system.git
cd pkm-system
```

2. Start containers

```bash
docker compose up --build
```

3. Access UI

```bash
Frontend → http://localhost:3000/ # local
Backend  → http://localhost:8000/ # local
```

4. Test

Upload files via UI, OR:

```bash
curl -F "file=@sample.pdf" http://localhost:8000/upload
```

### Evaluation Harness (Phase 3)

Supports latency and retrieval quality metrics:
    - hit@k
    - answer coverage
    - QA latency (p50, p95, p99)
    - TODO: Export Prometheus metrics for visualization in Grafana.

## Planned Features

| Feature                         | Description                              |
| ------------------------------- | ---------------------------------------- |
| Hybrid Retrieval (BM25 + FAISS) | Combine FTS5 keyword and semantic scores |

<!-- |Background Tasks|	Offload large document indexing using Celery| -->

|Auth & Multi-User Schema|	Per-user document isolation and roles|
|Knowledge Graph View|	Entity-relationship visualization of corpus|
|Cloud / On-Prem Deployment|	Configurable for both modes|

<!-- 🧠 Lessons Learned
Start small — modular feature development prevents overwhelm

Combining FAISS + SQLite makes vector + metadata persistence clean

Ollama simplifies running local LLMs (especially on Apple Silicon)

Evaluation and observability are crucial for RAG systems

A responsive UI transforms a backend prototype into a usable product -->

## Author

Rajat Gade

Early-career Software Engineer passionate about AI infrastructure, vector search, and scalable backend systems.
Actively exploring SWE / ML / AI roles — always open to collaborations!
