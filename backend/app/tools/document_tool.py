from app.retrieval.retriever import get_retriever


def search_documents(query: str, top_k: int = 5, filters: dict | None = None) -> list[dict]:
    chunks = get_retriever().retrieve(query, top_k=top_k, filters=filters)
    return [
        {"text": chunk.text, "metadata": chunk.metadata, "source": "document_rag", "score": chunk.score}
        for chunk in chunks
    ]
