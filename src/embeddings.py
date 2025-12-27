# src/embeddings.py
from sentence_transformers import SentenceTransformer
import numpy as np

# compact, fast model for PoC
MODEL_NAME = "all-MiniLM-L6-v2"

class EmbeddingModel:
    def __init__(self, model_name: str = MODEL_NAME):
        print("[embeddings] loading model:", model_name)
        self.model = SentenceTransformer(model_name)

    def embed(self, texts):
        """
        texts: list[str] -> returns numpy array (n, dim) dtype float32
        """
        arr = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return np.array(arr, dtype="float32")

if __name__ == "__main__":
    m = EmbeddingModel()
    print(m.embed(["hello world", "support ticket example"]).shape)
