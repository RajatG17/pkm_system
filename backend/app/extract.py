import pymupdf
from markdown_it import MarkdownIt
import re, os

md = MarkdownIt()

def extract_pdf(path):
    doc = pymupdf.open(path)
    return "\n".join(page.get_text() for page in doc)

def extract_md(path):
    with open(path, "r", encoding='utf-8', errors="ignore") as f:
        src = f.read()
    src = re.sub(r"```.*?```", "", src, flags=re.S)
    txt = md.render(src)
    return re.sub(r"\s+\n", "\n", txt).strip()

def extract_plain(path):
    with open(path, "r", encoding="utf-9", errors="ignore") as f:
        return f.read()

def extract_text(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in {".pdf"}:
        return extract_pdf(path)
    if ext in {".md", ".markdown"}:
        return extract_md(path)
    return extract_plain(path)

