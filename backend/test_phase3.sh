#!/usr/bin/env bash
set -euo pipefail

# ---- Config ----
BASE_URL="${BASE_URL:-http://localhost:8000}"
QUERY="${QUERY:-What is FAISS used for?}"
K="${K:-4}"
SAMPLE_FILE="${SAMPLE_FILE:-backend/uploads/hello.txt}"  # will be created if missing
TIMEOUT_SECS="${TIMEOUT_SECS:-180}"
SLEEP_SECS=2

export QUERY

have_jq() { command -v jq >/dev/null 2>&1; }

pp_json() {
  if have_jq; then jq -C . || cat; else cat; fi
}

log() { printf "\n\033[1m%s\033[0m\n" "$*"; }

# ---- 0) Health check (with retry/warmup) ----
log "0) Checking backend health at ${BASE_URL}/health ..."
deadline=$(( $(date +%s) + TIMEOUT_SECS ))
until curl -fsS "${BASE_URL}/health" >/dev/null 2>&1; do
  now=$(date +%s)
  if (( now > deadline )); then
    echo "Backend did not become healthy within ${TIMEOUT_SECS}s" >&2
    exit 1
  fi
  echo "Waiting for backend to be ready..."; sleep "${SLEEP_SECS}"
done
echo "Backend is healthy ✅"

# ---- 1) Ensure a sample file exists & upload (optional) ----
# If you already have files in uploads via the UI, you can skip this.
if [ ! -f "${SAMPLE_FILE}" ]; then
  log "1) Creating a tiny sample file at ${SAMPLE_FILE}"
  mkdir -p "$(dirname "${SAMPLE_FILE}")"
  cat > "${SAMPLE_FILE}" <<'EOF'
FAISS is a library for efficient similarity search and clustering of dense vectors. It is useful for nearest neighbor search over embeddings.
EOF
else
  log "1) Found existing sample file at ${SAMPLE_FILE}"
fi

log "1a) Uploading sample via API (/files/upload) ..."
# If your frontend already placed files into uploads, this simply duplicates;
# it's safe for testing. You can comment this out if you prefer.
UPLOAD_RES=$(curl -fsS -X POST \
  -F "file=@${SAMPLE_FILE}" \
  "${BASE_URL}/files/upload")
echo "$UPLOAD_RES" | pp_json

# ---- 2) Reindex (fresh build) ----
log "2) Rebuilding index via /index/reindex (first run may trigger Ollama model pull)..."
REINDEX_RES=$(curl -fsS -X POST "${BASE_URL}/index/reindex")
echo "$REINDEX_RES" | pp_json

# ---- 3) Smoke test: /search (optional) ----
log "3) Optional: quick search for 'faiss' via /search"
SEARCH_RES=$(curl -fsS "${BASE_URL}/search?q=faiss&k=${K}")
echo "$SEARCH_RES" | pp_json

# ---- 4) QA test: /qa ----
log "4) Asking QA: \"${QUERY}\""
QA_URL="${BASE_URL}/qa?q=$(python3 - <<PY
import urllib.parse, os
print(urllib.parse.quote(os.environ["QUERY"]))
PY
)"
QA_RES=$(curl -fsS "${QA_URL}&k=${K}")
echo "$QA_RES" | pp_json

# ---- 5) Friendly summary ----
if have_jq; then
  ANSWER=$(echo "$QA_RES" | jq -r '.answer // empty')
  echo
  log "Answer:"
  [ -n "$ANSWER" ] && echo "$ANSWER" || echo "(No answer field returned)"

  echo
  log "Top sources:"
  echo "$QA_RES" | jq -r '.sources[] | "- " + (.doc_path|tostring) + "#" + (.position|tostring) + "  (score: " + ((.score // 0)|tostring) + ")\n  " + (.preview // "")'
fi

echo
log "Done. Phase 3 looks good if you saw an answer and sources above ✅"
