from __future__ import annotations
import re
from typing import Iterable, List, Tuple, Optional
import tiktoken

_BLOCK_SEP_RE = re.compile(r"\n{2,}")  # paragraphs separated by blank lines
_CODE_FENCE_RE = re.compile(r"(^```.*?^```)", re.M | re.S)  # capture fenced code blocks
_WS_RE = re.compile(r"[ \t]+")

def _normalize(text: str) -> str:
    # normalize whitespace but keep newlines (structure)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _WS_RE.sub(" ", text)
    # collapse >2 newlines to exactly two
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def _split_into_blocks(text: str) -> List[str]:
    """
    Split text into logical blocks: fenced code blocks stay intact;
    everything else is split on paragraph boundaries (blank lines).
    """
    parts: List[str] = []
    pos = 0
    for m in _CODE_FENCE_RE.finditer(text):
        before = text[pos:m.start()]
        fence = m.group(1)
        if before.strip():
            parts.extend([b for b in _BLOCK_SEP_RE.split(before) if b.strip()])
        parts.append(fence.strip())
        pos = m.end()
    tail = text[pos:]
    if tail.strip():
        parts.extend([b for b in _BLOCK_SEP_RE.split(tail) if b.strip()])
    return parts

def _encode(enc, s: str) -> List[int]:
    return enc.encode(s)

def _decode(enc, toks: List[int]) -> str:
    return enc.decode(toks)

def chunk_text(
    text: str,
    target_tokens: int = 350,
    overlap_tokens: int = 50,
    min_chunk_tokens: int = 40,
    enc_name: str = "cl100k_base",
) -> List[str]:
    """
    Pack blocks into chunks up to target_tokens, keep code fences intact,
    and add token overlap between adjacent chunks. Returns non-empty chunks.
    """
    if not text or not text.strip():
        return []

    text = _normalize(text)
    blocks = _split_into_blocks(text)
    enc = tiktoken.get_encoding(enc_name)

    chunks: List[List[int]] = []
    cur: List[int] = []

    def flush():
        nonlocal cur
        if not cur:
            return
        if len(cur) >= min_chunk_tokens:
            chunks.append(cur)
        else:
            # if too small, merge into previous if exists
            if chunks:
                chunks[-1].extend(cur)
            else:
                chunks.append(cur)  # first and tiny – still keep it
        cur = []

    for block in blocks:
        btoks = _encode(enc, block)
        # If single block is huge, hard-split on token count boundaries
        if len(btoks) > target_tokens * 2:
            start = 0
            while start < len(btoks):
                end = min(start + target_tokens, len(btoks))
                segment = btoks[start:end]
                # if there is a remainder and not first segment, add overlap
                if start > 0 and overlap_tokens > 0:
                    prev_tail = btoks[max(0, start - overlap_tokens):start]
                    segment = prev_tail + segment
                # push current if accumulating something
                if cur:
                    flush()
                chunks.append(segment)
                start = end
            continue

        # Try to pack block into current buffer
        if len(cur) + len(btoks) <= target_tokens:
            cur.extend(btoks)
        else:
            # flush current with overlap into next
            flush()
            if overlap_tokens > 0 and chunks:
                # seed cur with overlap from previous chunk tail
                tail = chunks[-1][-overlap_tokens:]
                cur.extend(tail)
            # add the block (might still exceed, handled next iteration)
            if len(btoks) > target_tokens and not cur:
                # very large block that didn't hit >2*target (rare):
                # split it reasonably
                start = 0
                while start < len(btoks):
                    end = min(start + target_tokens, len(btoks))
                    seg = btoks[start:end]
                    if start > 0 and overlap_tokens > 0:
                        seg = btoks[max(0, start - overlap_tokens):start] + seg
                    chunks.append(seg)
                    start = end
            else:
                cur.extend(btoks)

    flush()

    # decode, strip empties
    out = [_decode(enc, c).strip() for c in chunks]
    out = [c for c in out if c and not c.isspace()]
    return out