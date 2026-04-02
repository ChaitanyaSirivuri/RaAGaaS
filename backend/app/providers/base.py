from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class VectorUpsert:
    """Single vector row for upsert into a vector store."""

    uuid: str
    vector: list[float]
    properties: dict[str, Any]


@dataclass
class SearchResult:
    text: str
    score: float
    metadata: dict[str, Any]


class VectorProvider(ABC):
    @abstractmethod
    async def create_collection(self, name: str, dim: int) -> None:
        """Create or ensure a collection/class exists with vector dimension `dim`."""

    @abstractmethod
    async def upsert(self, collection: str, vectors: list[VectorUpsert]) -> None:
        """Insert or replace vectors in `collection`."""

    @abstractmethod
    async def search(
        self, collection: str, query_vec: list[float], top_k: int
    ) -> list[SearchResult]:
        """Nearest-neighbor search in `collection`."""

    @abstractmethod
    async def delete_collection(self, name: str) -> None:
        """Remove the entire collection/class."""


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one embedding vector per input text (same order)."""

    @property
    @abstractmethod
    def dim(self) -> int:
        """Embedding dimensionality."""


class RerankerProvider(ABC):
    @abstractmethod
    async def rerank(self, query: str, docs: list[str]) -> list[float]:
        """Return relevance scores aligned with `docs` (stub in v1)."""
