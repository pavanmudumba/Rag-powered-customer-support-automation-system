# src/index_sklearn.py
import os, pickle
from src.ingest import ingest_folder

from src.embeddings import EmbeddingModel
import numpy as np
from sklearn.neighbors import NearestNeighbors

INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "sklearn_index.pkl")
META_PATH = os.path.join(os.path.dirname(__file__), "..", "sklearn_meta.pkl")

def build_index(folder="sample_docs"):
    print("[sklearn] ingesting docs...")
    docs = ingest_folder(folder)
    texts = []
    metas = []
    for d in docs:
        fn = d["meta"].get("filename", "unknown")
        for i, chunk in enumerate(d["chunks"]):
            texts.append(chunk)
            metas.append({"filename": fn, "chunk_index": i, "text": chunk})
    if len(texts) == 0:
        raise ValueError("No texts found in sample_docs.")
    print(f"[sklearn] {len(texts)} chunks to embed")
    emb = EmbeddingModel()
    vectors = emb.embed(texts).astype("float32")
    nbrs = NearestNeighbors(metric="cosine", algorithm="auto", n_jobs=-1)
    nbrs.fit(vectors)
    with open(INDEX_PATH, "wb") as f:
        pickle.dump(nbrs, f)
    with open(META_PATH, "wb") as f:
        pickle.dump(metas, f)
    print(f"[sklearn] index built with {len(metas)} vectors (dim={vectors.shape[1]})")

def search(query, top_k=5):
    """
    Return list of {score, meta} for up to top_k nearest chunks.
    This function safely caps requested neighbors to the number of indexed samples.
    """
    if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
        raise RuntimeError("Index or meta not found. Run build_index() first (or call /rebuild).")

    emb = EmbeddingModel()
    qv = emb.embed([query]).astype("float32")

    with open(INDEX_PATH, "rb") as f:
        nbrs = pickle.load(f)

    # number of samples in the fitted index
    # sklearn stores fitted data in attribute _fit_X (private) - fall back to length of metas if needed
    n_samples = None
    try:
        n_samples = getattr(nbrs, "_fit_X", None)
        if n_samples is not None:
            n_samples = n_samples.shape[0]
    except Exception:
        n_samples = None

    # fallback to meta length
    if n_samples is None:
        with open(META_PATH, "rb") as f:
            metas = pickle.load(f)
        n_samples = len(metas)
    else:
        with open(META_PATH, "rb") as f:
            metas = pickle.load(f)

    # cap k
    k = max(1, min(top_k, n_samples))

    distances, indices = nbrs.kneighbors(qv, n_neighbors=k)
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        meta = metas[int(idx)]
        score = float(1.0 - dist)  # convert distance->similarity-ish
        results.append({"score": score, "meta": meta})
    return results


if __name__ == "__main__":
    build_index("sample_docs")
    print(search("How do I reset my password?", top_k=5))
