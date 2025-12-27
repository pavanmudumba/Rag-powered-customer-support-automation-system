# src/chroma_index.py

from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
import os

print("🔎 CWD:", os.getcwd())

# ----------------------------
# Paths
# ----------------------------
DOCS_DIR = Path("knowledge_base/docs").resolve()
CHROMA_DIR = Path("chroma_db").resolve()

# ----------------------------
# Constants
# ----------------------------
CHUNK_SIZE = 500
COLLECTION_NAME = "knowledge_base"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def build_chroma_index():
    print("📁 Docs dir:", DOCS_DIR)
    print("📦 Chroma dir:", CHROMA_DIR)

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    # ✅ MUST USE PersistentClient
    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn
    )

    documents, metadatas, ids = [], [], []

    files = list(DOCS_DIR.glob("*.txt"))
    print("📄 Files found:", [f.name for f in files])

    for file in files:
        text = file.read_text(encoding="utf-8").strip()
        if not text:
            continue

        chunks = [
            text[i:i + CHUNK_SIZE]
            for i in range(0, len(text), CHUNK_SIZE)
            if text[i:i + CHUNK_SIZE].strip()
        ]

        for idx, chunk in enumerate(chunks):
            documents.append(chunk)
            metadatas.append({
                "source_file": file.name,
                "chunk_index": idx
            })
            ids.append(f"{file.stem}__chunk_{idx}")

    if not documents:
        raise RuntimeError("❌ No documents to index")

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print(f"✅ Indexed {len(documents)} chunks")
    print(f"📦 Chroma persisted at: {CHROMA_DIR}")


if __name__ == "__main__":
    build_chroma_index()
