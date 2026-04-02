import re

from app.chunking.base import Chunk, ChunkConfig, ChunkingStrategy
from app.chunking.fixed import FixedChunker


class RecursiveChunker(ChunkingStrategy):
    """Split on paragraph boundaries first, then apply fixed token windows per block."""

    def __init__(self) -> None:
        self._fixed = FixedChunker()

    def chunk(self, text: str, config: ChunkConfig) -> list[Chunk]:
        if not text.strip():
            return []
        blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
        if not blocks:
            blocks = [text.strip()]
        out: list[Chunk] = []
        idx = 0
        for block in blocks:
            for ch in self._fixed.chunk(block, config):
                out.append(
                    Chunk(
                        text=ch.text,
                        index=idx,
                        token_start=ch.token_start,
                        token_end=ch.token_end,
                    ),
                )
                idx += 1
        return out
