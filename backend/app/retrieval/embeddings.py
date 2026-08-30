from functools import lru_cache

from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()


@lru_cache
def get_embedding_model(model_name: str) -> EmbeddingModel:
    return EmbeddingModel(model_name)
