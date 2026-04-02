from app.providers.base import SearchResult, VectorProvider, VectorUpsert


class ChromaProvider(VectorProvider):
    async def create_collection(self, name: str, dim: int) -> None:
        raise NotImplementedError("ChromaProvider is a stub for v2")

    async def upsert(self, collection: str, vectors: list[VectorUpsert]) -> None:
        raise NotImplementedError("ChromaProvider is a stub for v2")

    async def search(
        self, collection: str, query_vec: list[float], top_k: int
    ) -> list[SearchResult]:
        raise NotImplementedError("ChromaProvider is a stub for v2")

    async def delete_collection(self, name: str) -> None:
        raise NotImplementedError("ChromaProvider is a stub for v2")
