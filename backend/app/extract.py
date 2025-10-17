from __future__ import annotations
import os, re, io, chardet
import fitz
from markdown_it import MarkdownIt

md = MarkdownIt()

_HEADER_FOOTER_RE = re.compile(r"(^.{0,80}\s*\n){0,2}|(\n.{0,80}$){0,2}", re.M)
HYPHEN_LINEBREAK = re.compile(r"(\w)-\n(\w)")
MULTISPACE = re.compile(r"[ \t]+")

def _normalize_text(t: str):
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    t = HYPHEN_LINEBREAK.sub(r"\1\2",t)
    t = MULTISPACE.sub(" ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()

def _real_text_guess_encoding(path: str):
    with open(path, "rb") as f:
        raw = f.read()
    enc = chardet.detect(raw).get("encoding") or "utf-8"
    try:
        return raw.decode(enc, errors="ignore")
    except Exception:
        return raw.decode("utf-8", errors="ignore")
    
def extract_pdf(path: str):
    doc = fitz.open(path)
    pages = []
    for p in doc:
        txt = p.get_text("text")
        txt = _HEADER_FOOTER_RE.sub("", txt)
        pages.append(txt.strip())
    out = "\n\n".join(pages)
    return _normalize_text(out)

def extract_md(path):
    src = _real_text_guess_encoding(path)
    htmlish = md.render(src)
    text = re.sub(r"<[^>]+>", "", htmlish)
    text = re.sub(r"http[s]?://\S+", "", text)
    return _normalize_text(text)

def extract_code(path):
    return _normalize_text(_real_text_guess_encoding(path))

def extract_plain(path):
    return _normalize_text(_real_text_guess_encoding(path))

def extract_text(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return extract_pdf(path)
    if ext in {".md", ".markdown"}:
        return extract_md(path)
    if ext in {".py", ".js", ".ts", ".tsx", ".java", ".go", ".rs", ".cpp", ".c", ".h", ".cs", ".rb", ".php", ".scala", ".kt", ".sql"}:
        return extract_code(path)
    return extract_plain(path)