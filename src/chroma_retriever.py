# src/chroma_retriever.py

from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

CHROMA_DIR = Path("chroma_db").resolve()
COLLECTION_NAME = "knowledge_base"

if not CHROMA_DIR.exists():
    raise RuntimeError(
        f"❌ Chroma DB not found at {CHROMA_DIR}. Run chroma_index.py first."
    )

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# ✅ MUST USE PersistentClient
client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

collection = client.get_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_fn
)


def retrieve_context(query: str, top_k: int = 5):
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    contexts = []

    if not results or not results["documents"] or not results["documents"][0]:
        return contexts

    for i in range(len(results["documents"][0])):
        distance = results["distances"][0][i]
        similarity = round(max(0.0, 1.0 - distance), 3)

        contexts.append({
            "text": results["documents"][0][i],
            "meta": results["metadatas"][0][i],
            "score": similarity
        })

    return contexts


if __name__ == "__main__":
    print("🔎 Testing retrieval...")
    res = retrieve_context("What are the symptoms of diabetes?")
    print("Results:", len(res))
    for r in res:
        print(r["score"], r["meta"])
