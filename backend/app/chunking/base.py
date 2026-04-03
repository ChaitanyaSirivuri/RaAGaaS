from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ChunkConfig:
    strategy: str
    size: int
    overlap: int


@dataclass
class Chunk:
    text: str
    index: int
    token_start: int
    token_end: int


class ChunkingStrategy(ABC):
    @abstractmethod
    def chunk(self, text: str, config: ChunkConfig) -> list[Chunk]:
        """Split `text` into chunks according to `config`."""
