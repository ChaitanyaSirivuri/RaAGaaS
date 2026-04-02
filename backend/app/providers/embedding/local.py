from app.providers.base import EmbeddingProvider


class LocalEmbedding(EmbeddingProvider):
    @property
    def dim(self) -> int:
        raise NotImplementedError("LocalEmbedding is a stub for v2")

    async def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError("LocalEmbedding is a stub for v2")
