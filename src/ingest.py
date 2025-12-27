# src/ingest.py
import os
from typing import List
from pypdf import PdfReader
import docx
import re

def extract_text_from_pdf(path: str) -> str:
    text = []
    reader = PdfReader(path)
    for p in reader.pages:
        text.append(p.extract_text() or "")
    return "\n".join(text)

def extract_text_from_docx(path: str) -> str:
    doc = docx.Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def extract_text(path: str) -> str:
    path = os.path.abspath(path)
    if path.lower().endswith(".pdf"):
        return extract_text_from_pdf(path)
    if path.lower().endswith(".docx"):
        return extract_text_from_docx(path)
    # fallback: treat as text
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def clean_text(s: str) -> str:
    s = re.sub(r"\r\n", "\n", s)
    s = re.sub(r"\n{2,}", "\n\n", s)
    return s.strip()

def chunk_text(text: str, chunk_size_tokens: int = 500, overlap_tokens: int = 100) -> List[str]:
    words = text.split()
    chunks = []
    i = 0
    n = len(words)
    while i < n:
        j = min(i + chunk_size_tokens, n)
        chunk = " ".join(words[i:j])
        chunks.append(chunk)
        i = j - overlap_tokens if (j - overlap_tokens) > i else j
    return chunks

def ingest_folder(folder_path: str):
    docs = []
    for fn in os.listdir(folder_path):
        full = os.path.join(folder_path, fn)
        if not os.path.isfile(full):
            continue
        try:
            raw = extract_text(full)
            raw = clean_text(raw)
            chunks = chunk_text(raw)
            meta = {"filename": fn, "path": full}
            docs.append({"meta": meta, "chunks": chunks})
            print(f"[ingest] {fn} -> {len(chunks)} chunks")
        except Exception as e:
            print(f"[ingest] failed {fn}: {e}")
    return docs
