from functools import lru_cache

from app.config.settings import Settings, get_settings
from app.models.evidence import EvidenceChunk
from app.reranking.reranker import get_reranker
from app.retrieval.bm25_retriever import BM25Retriever
from app.retrieval.embeddings import get_embedding_model
from app.retrieval.vector_store import ChromaVectorStore

RRF_K = 60


def _matches_filters(metadata: dict, filters: dict | None) -> bool:
    if not filters:
        return True
    return all(metadata.get(key) == value for key, value in filters.items())


def _reciprocal_rank_fusion(*ranked_id_lists: list[str], k: int = RRF_K) -> dict[str, float]:
    scores: dict[str, float] = {}
    for ranked_ids in ranked_id_lists:
        for rank, doc_id in enumerate(ranked_ids):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    return scores


class Retriever:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.embedding_model = get_embedding_model(settings.embedding_model)
        self.vector_store = ChromaVectorStore(settings.chroma_persist_dir)
        self.bm25 = BM25Retriever(self.vector_store)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: dict | None = None,
        candidate_k: int = 20,
    ) -> list[EvidenceChunk]:
        if self.vector_store.count() == 0:
            return []

        query_embedding = self.embedding_model.embed([query])[0]
        dense_results = self.vector_store.query(query_embedding, top_k=candidate_k)
        dense_ids = dense_results["ids"][0]

        pool: dict[str, tuple[str, dict]] = dict(
            zip(dense_ids, zip(dense_results["documents"][0], dense_results["metadatas"][0]))
        )

        bm25_hits = self.bm25.search(query, top_k=candidate_k)
        bm25_ids = [hit[0] for hit in bm25_hits]
        for doc_id, doc, meta, _score in bm25_hits:
            pool.setdefault(doc_id, (doc, meta))

        fused_scores = _reciprocal_rank_fusion(dense_ids, bm25_ids)
        ranked_ids = [
            doc_id
            for doc_id, _score in sorted(fused_scores.items(), key=lambda kv: kv[1], reverse=True)
            if _matches_filters(pool[doc_id][1], filters)
        ]

        candidates = [
            EvidenceChunk(text=pool[doc_id][0], metadata=pool[doc_id][1], score=fused_scores[doc_id])
            for doc_id in ranked_ids
        ]
        if not candidates:
            return []

        reranker = get_reranker(self.settings.reranker_model)
        return reranker.rerank(query, candidates, top_k=top_k)

    def retrieve_dense_only(self, query: str, top_k: int = 5) -> list[EvidenceChunk]:
        """Basic vector-only retrieval (no BM25, no fusion, no reranking) — the
        Phase 1 baseline, kept as an explicit comparison point for evaluation
        (skills.md section 14: 'Compare Multiple RAG Versions')."""
        if self.vector_store.count() == 0:
            return []
        query_embedding = self.embedding_model.embed([query])[0]
        results = self.vector_store.query(query_embedding, top_k=top_k)
        return [
            EvidenceChunk(text=doc, metadata=meta, score=1 - dist)
            for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0])
        ]


@lru_cache
def get_retriever() -> Retriever:
    return Retriever(get_settings())
