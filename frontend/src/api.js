const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function search(q, k=5) {
    const url = new URL(`${API_BASE}/search`);
    url.searchParams.set("q", q);
    url.searchParams.set("k", k);
    const r = await fetch(url);
    if (!r.ok) throw new Error(`Search failes: ${r.status}`);
    return r.json();
}

export async function qa(q, k=4, maxCtxChars = 1800) {
    const url = new URL(`${API_BASE}/qa`);
    url.searchParams.set("q",q);
    url.searchParams.set("k", k);
    url.searchParams.set("max_ctx_chars", maxCtxChars);
    const r = await fetch(url);
    if (!r.ok) throw new Error(`QA failed: ${r.status}`);
    return r.json();
}

export async function uploadFile(file) {
    const fd = new FormData();
    fd.append("file", file);
    const r = await fetch(`${API_BASE}/files/upload`, {method: "POST", body: fd});
    if (!r.ok) throw new Error(`Upload failed: ${r.status}`);
    return r.json();
}

export async function reindex() {
    const r = await fetch(`${API_BASE}/index/reindex`, {method: "POST"});
    if (!r.ok) throw new Error(`Reindex failed: ${r.status}`);
    return r.json();
}

export async function incremental() {
    const r = await fetch(`${API_BASE}/index/incremental`, {method: "POST"});
    if (!r.ok) throw new Error(`Incremental failed: ${r.status}`);
    return r.json();
}

export async function health() {
    const r = await fetch(`${API_BASE}/health`);
    return r.ok;
}