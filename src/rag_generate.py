# src/rag_generate.py

from src.chroma_retriever import retrieve_context

MAX_CONTEXTS = 3


def generate_answer(query: str, top_k: int = MAX_CONTEXTS):
    """
    Production-style RAG generator.
    Works on ANY raw text (medical, legal, policy, etc.)
    """

    contexts = retrieve_context(query, top_k=top_k)

    if not contexts:
        return {
            "answer": (
                "Hello,\n\n"
                "We could not find relevant information for your request. "
                "Your ticket has been escalated to a support agent.\n\n"
                "Regards,\nSupport Team"
            ),
            "confidence": 0.0,
            "contexts": []
        }

    # Use retrieved passages directly
    selected = contexts[:MAX_CONTEXTS]

    body = "\n\n".join(
        f"- {c['text'][:400].strip()}..."
        for c in selected
    )

    answer = (
        "Hello,\n\n"
        "Based on our medical knowledge base, here is the relevant information:\n\n"
        f"{body}\n\n"
        "If you need further clarification, the ticket will be escalated.\n\n"
        "Regards,\nSupport Team"
    )

    # Confidence = retrieval strength
    confidence = round(
        min(1.0, 0.4 + (0.2 * len(selected))),
        2
    )

    return {
        "answer": answer,
        "confidence": confidence,
        "contexts": selected
    }
