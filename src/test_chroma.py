# src/test_chroma.py

from src.chroma_retriever import retrieve_context

query = "How do I reset my password?"

results = retrieve_context(query)

for r in results:
    print("TEXT:", r["text"][:100])
    print("META:", r["meta"])
    print("SCORE:", r["score"])
    print("-" * 40)
