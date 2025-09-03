import tiktoken

def chunk_text(text, target_tokens=300, overlap=50, enc_name="cl100k_base"):
    enc = tiktoken.get_encoding(enc_name)
    toks = enc.encode(text)
    out = []
    start = 0
    while start < len(toks):
        end = min(start + target_tokens, len(toks))
        piece = enc.decode(toks[start:end])
        out.append(piece)
        if end == len(toks):
            break
        start = max(end - overlap, 0)

    return out
