from functools import lru_cache

from sentence_transformers import CrossEncoder

from app.models.evidence import EvidenceChunk


class Reranker:
    def __init__(self, model_name: str):
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, candidates: list[EvidenceChunk], top_k: int) -> list[EvidenceChunk]:
        if not candidates:
            return []
        pairs = [(query, c.text) for c in candidates]
        scores = self.model.predict(pairs)
        reranked = sorted(zip(candidates, scores), key=lambda pair: pair[1], reverse=True)
        return [
            EvidenceChunk(text=chunk.text, metadata=chunk.metadata, score=float(score))
            for chunk, score in reranked[:top_k]
        ]


@lru_cache
def get_reranker(model_name: str) -> Reranker:
    return Reranker(model_name)
