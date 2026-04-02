from openai import AsyncOpenAI

from app.providers.base import EmbeddingProvider


class OpenAIEmbedding(EmbeddingProvider):
    """OpenAI text embedding models (e.g. text-embedding-3-small)."""

    _DIMS: dict[str, int] = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
    }

    def __init__(self, api_key: str, model: str) -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    @property
    def dim(self) -> int:
        return self._DIMS.get(self._model, 1536)

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        resp = await self._client.embeddings.create(model=self._model, input=texts)
        out: list[list[float]] = [[] for _ in texts]
        for item in resp.data:
            out[item.index] = list(item.embedding)
        return out
