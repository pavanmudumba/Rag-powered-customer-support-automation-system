# src/app_faiss.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import traceback
import threading
import importlib

app = FastAPI(title="RAG PoC - Index Retrieval (lazy init, package-safe)")

_singletons = {}
_singleton_lock = threading.Lock()

def ensure_module(module_name: str):
    """
    Import a module using full package path (src.<module>) if available,
    otherwise try plain module_name. Return imported module object.
    """
    # prefer explicit package import
    try:
        full_name = f"src.{module_name}"
        return importlib.import_module(full_name)
    except ModuleNotFoundError:
        # fallback to top-level import (useful if you run differently)
        return importlib.import_module(module_name)

def get_embedding_model():
    if "emb_model" in _singletons:
        return _singletons["emb_model"]
    with _singleton_lock:
        if "emb_model" in _singletons:
            return _singletons["emb_model"]
        # import lazily using package-safe loader
        mod = ensure_module("embeddings")
        EmbeddingModel = getattr(mod, "EmbeddingModel")
        _singletons["emb_model"] = EmbeddingModel()
        return _singletons["emb_model"]

def get_search_fn():
    if "search_fn" in _singletons:
        return _singletons["search_fn"]
    with _singleton_lock:
        if "search_fn" in _singletons:
            return _singletons["search_fn"]
        # try index_faiss, then sklearn, then hnsw - using package-safe imports
        for candidate in ("index_faiss", "index_sklearn", "index_hnsw"):
            try:
                mod = ensure_module(candidate)
                if hasattr(mod, "search"):
                    _singletons["search_fn"] = getattr(mod, "search")
                    # also capture build_index if present
                    _singletons["build_index_fn"] = getattr(mod, "build_index", None)
                    return _singletons["search_fn"]
            except ModuleNotFoundError:
                continue
        raise RuntimeError("No index backend available. Ensure index_faiss.py or index_sklearn.py exists in src/")

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

@app.post("/query")
def query(req: QueryRequest):
    try:
        # lazy init
        _ = get_embedding_model()    # ensure model loaded (if needed)
        search_fn = get_search_fn()
        results = search_fn(req.query, top_k=req.top_k)
        return {"query": req.query, "results": results}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rebuild")
def rebuild():
    try:
        # try to call a build_index function from whichever module we loaded
        # this was stored in singletons by get_search_fn
        build_fn = _singletons.get("build_index_fn", None)
        if build_fn is not None:
            build_fn("sample_docs")
            return {"status": "ok", "message": "index rebuilt via backend build_index"}
        # fallback: try to import explicit module builders
        for candidate in ("index_faiss", "index_sklearn", "index_hnsw"):
            try:
                mod = ensure_module(candidate)
                if hasattr(mod, "build_index"):
                    getattr(mod, "build_index")("sample_docs")
                    return {"status": "ok", "message": f"index rebuilt via {candidate}.build_index"}
            except ModuleNotFoundError:
                continue
        raise RuntimeError("No index builder found in available backends.")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
