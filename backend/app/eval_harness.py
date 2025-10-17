import argparse, os, sys, time, csv, re, json
from typing import List, Dict, Any
import requests

try:
    import yaml
except Exception:
    print("Mising PyAML, Install it", file=sys.stderr)
    sys.exit(1)

def load_yaml(path):
    with open(path, "r", encoding='utf-8') as f:
        data = yaml.safe_load(f)
    if not isinstance(data, list):
        raise ValueError("YAML root must br a list of questions")
    return data

def call_qa(base_url, q, k, max_ctx, timeout_s):
    r = requests.get(
        f"{base_url}/qa",
        params={"q":q, "k":k, "max_ctx_chars":max_ctx},
        timeout=timeout_s,
    )
    r.raise_for_status()
    return r.json()

def fetch_metrics(base_url):
    try:
        r = requests.get(f"{base_url}/metrics", timeout=10)
        if r.status_code != 200:
            return {}
        text = r.text
        vals = {}
        for name in ["qa_latency_ms_p50", "qa_latency_ms_p95", "search_latency_ms_p50", "search_latency_ms_p95"]:
            m = re.search(rf"^{name}\s+([0-9.]+)$", text, flags=re.M)
            if m:
                vals[name] = float(m.group(1))
        return vals
    except Exception:
        return {}
    
def normalize(s):
    return re.sub(r"\s+", " ", (s or "")).strip().lower()

def answer_is_grounded(ans):
    s = normalize(ans)
    if not s:
        return False
    return not any(neg in s for neg in ["i dont know", "i do not know", "not in the provided", "no context", "cannot find", "insufficient context"])

def eval_hitk(sources, expect):
    """
    Return True if any source matches expectation
    """
    if not sources:
        return False
    doc_path = expect.get("doc_path")
    position = expect.get("position")
    pos_radius = int(expect.get("pos_radius", 0))
    contains = [c.lower() for c in (expect.get("contains") or [])]

    for s in sources:
        ok = True
        if doc_path:
            if doc_path == s.get("doc_path"):
                pass
            elif doc_path in (s.get("doc_path") or ""):
                pass
            else:
                ok = False
        if ok and position is not None:
            pos = int(s.get("position", -999999))
            if abs(pos-int(position)) > pos_radius:
                ok = False
        if ok and contains:
            preview = (s.get("preview") or "").lower()
            if not any(c in preview for c in contains):
                ok = False
        if ok:
            return True
    
    return False

def run(base_url, yaml_path, out_prefix, timeout_s):
    rows = load_yaml(yaml_path)
    results = []
    hit_count = 0
    grounded_count = 0

    for i, row in enumerate(rows, 1):
        q = row["q"]
        k = int(row.get("k", 4))
        max_ctx = int(row.get("mat_ctx_chars", 2000))
        expect = row.get("expect", {}) or {}

        t0 = time.perf_counter()
        try:
            qa = call_qa(base_url, q, k, max_ctx, timeout_s)
            elapsed = (time.perf_counter() - t0) * 1000.0
            ans = qa.get("answer", "")
            sources = qa.get("sources", [])
            grounded = answer_is_grounded(ans)
            hitk = eval_hitk(sources, expect) if expect else None
            if grounded: grounded_count += 1
            if hitk: hit_count += 1
            results.append({
                "idx": i, "q": q, "k": k, "max_ctx_chars": max_ctx,
                "hit@k": hitk, "grounded_answer": grounded,
                "latency_ms": round(elapsed, 1),
                "n_sources": len(sources),
                "top_source": (sources[0]["doc_path"] + f"#{sources[0]['position']}") if sources else "",
                "answer": ans.strip(),                               
            })
            print(f"[{i}/{len(rows)}] hit@k={hitk} grounded={grounded} latency={elapsed:.1f}ms  q={q[:60]}")
        except requests.Timeout:
            results.append({"idx": i, "q": q, "error": "timeout"})
            print(f"[{i}/{len(rows)}] TIMEOUT  q={q}")
        except Exception as e:
            results.append({"idx": i, "q": q, "error": str(e)})
            print(f"[{i}/{len(rows)}] ERROR {e}  q={q}")
        
    csv_path = f"{out_prefix}_results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        for r in results: w.writerow(r)

    # Aggregate
    total = len(rows)
    metrics = fetch_metrics(base_url)
    hit_ratio = (hit_count / total) if total and any(r.get("hit@k") is not None for r in results) else None
    grounded_ratio = grounded_count / total if total else 0.0

    summary = {
        "total_questions": total,
        "hit_at_k": hit_ratio,
        "answer_coverage": grounded_ratio,
        "qa_p50_ms": metrics.get("qa_latency_ms_p50"),
        "qa_p95_ms": metrics.get("qa_latency_ms_p95"),
        "search_p50_ms": metrics.get("search_latency_ms_p50"),
        "search_p95_ms": metrics.get("search_latency_ms_p95"),
    }
    json_path = f"{out_prefix}_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Markdown summary
    md = [
      "# RAG Evaluation Summary",
      "",
      f"- **Total questions:** {total}",
      f"- **Hit@K:** {None if hit_ratio is None else f'{hit_ratio*100:.1f}%'}",
      f"- **Answer coverage:** {grounded_ratio*100:.1f}%",
      f"- **QA latency p50/p95:** {metrics.get('qa_latency_ms_p50','–')} ms / {metrics.get('qa_latency_ms_p95','–')} ms",
      f"- **Search latency p50/p95:** {metrics.get('search_latency_ms_p50','–')} ms / {metrics.get('search_latency_ms_p95','–')} ms",
      "",
      "## Notes",
      "- *Hit@K counts a success if any returned source matches your expected document (and optional position/substring).*",
      "- *Answer coverage counts an answer unless it says “I don't know …”.*",
      "",
      "## Per-question (first few)",
      ""
    ]
    for r in results[:5]:
        md.append(f"- **Q:** {r.get('q')}")
        md.append(f"  - hit@k: {r.get('hit@k')}  · grounded: {r.get('grounded_answer')}  · latency: {r.get('latency_ms','–')} ms")
        md.append(f"  - top source: {r.get('top_source','')}")
        md.append("")
    md_path = f"{out_prefix}_summary.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print("\n=== SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print(f"\nWrote:\n- {csv_path}\n- {json_path}\n- {md_path}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=os.getenv("BASE_URL","http://localhost:8000"), help="Backend base URL")
    ap.add_argument("--yaml", default="questions.yaml", help="Path to questions YAML")
    ap.add_argument("--out", default="eval", help="Output prefix")
    ap.add_argument("--timeout", type=float, default=float(os.getenv("QA_TIMEOUT","300")), help="Per-request timeout (s)")
    args = ap.parse_args()
    run(args.base_url, args.yaml, args.out, args.timeout)



