def build_qa_prompt(question: str, contexts: list[dict]) -> str:
    """
    contexts: list of metadata dicts for retrieved chunks. Must include
    'text_preview' and optionally 'doc_path'/'position'.
    """
    ctx_txt = []
    for i, c in enumerate(contexts, start=1):
        preview = c.get("text_preview", "").strip()
        origin = c.get("doc_path", "unknown")
        pos = c.get("position", 0)
        # Keep each snippet tidy
        snippet = preview.replace("\n\n", "\n").strip()
        ctx_txt.append(f"[{i}] ({origin}#{pos})\n{snippet}")
    ctx_block = "\n\n---\n\n".join(ctx_txt)

    return f"""You are a precise assistant. Use ONLY the provided context to answer.
If the answer is not in the context, say "I don't know from the provided documents."

Question:
{question}

Context:
{ctx_block}

Instructions:
- Be concise (3–6 sentences).
- Cite sources inline like [1], [2].
- If multiple sources support a claim, cite all relevant ones.
- Do not invent facts outside the context.

Answer:"""