import chromadb


class ChromaVectorStore:
    def __init__(self, persist_dir: str, collection_name: str = "documents"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(collection_name)

    def add(self, ids: list[str], texts: list[str], embeddings: list[list[float]], metadatas: list[dict]) -> None:
        if not ids:
            return
        self.collection.upsert(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)

    def query(self, query_embedding: list[float], top_k: int = 5, where: dict | None = None) -> dict:
        kwargs: dict = {"query_embeddings": [query_embedding], "n_results": top_k}
        if where:
            kwargs["where"] = where
        return self.collection.query(**kwargs)

    def get_all(self) -> tuple[list[str], list[str], list[dict]]:
        result = self.collection.get(include=["documents", "metadatas"])
        return result["ids"], result["documents"], result["metadatas"]

    def count(self) -> int:
        return self.collection.count()
