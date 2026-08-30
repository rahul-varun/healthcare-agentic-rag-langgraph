import re

from rank_bm25 import BM25Okapi

from app.retrieval.vector_store import ChromaVectorStore

_TOKEN_RE = re.compile(r"\w+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class BM25Retriever:
    """Sparse retrieval over the same corpus stored in the vector store.

    rank_bm25 keeps its index in memory only, so we rebuild it from whatever the
    vector store currently holds. Fine at dev scale (see spec: ChromaDB is the
    dev-only vector DB) — a production BM25 index would live in Postgres FTS or
    a dedicated search engine instead of being rebuilt per Retriever instance.
    """

    def __init__(self, vector_store: ChromaVectorStore):
        self.ids, self.documents, self.metadatas = vector_store.get_all()
        tokenized_corpus = [_tokenize(doc) for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_corpus) if tokenized_corpus else None

    def search(self, query: str, top_k: int) -> list[tuple[str, str, dict, float]]:
        if self.bm25 is None:
            return []
        scores = self.bm25.get_scores(_tokenize(query))
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [
            (self.ids[i], self.documents[i], self.metadatas[i], float(scores[i]))
            for i in ranked_indices
            if scores[i] > 0
        ]
