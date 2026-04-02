import tiktoken

from app.chunking.base import Chunk, ChunkConfig, ChunkingStrategy


class FixedChunker(ChunkingStrategy):
    """Token-based fixed windows with overlap (cl100k_base)."""

    def __init__(self) -> None:
        self._enc = tiktoken.get_encoding("cl100k_base")

    def chunk(self, text: str, config: ChunkConfig) -> list[Chunk]:
        if not text.strip():
            return []
        tokens = self._enc.encode(text)
        if not tokens:
            return []
        size = max(1, config.size)
        overlap = min(max(0, config.overlap), size - 1)
        step = size - overlap
        chunks: list[Chunk] = []
        idx = 0
        start = 0
        while start < len(tokens):
            end = min(start + size, len(tokens))
            window = tokens[start:end]
            piece = self._enc.decode(window)
            chunks.append(
                Chunk(text=piece, index=idx, token_start=start, token_end=end),
            )
            idx += 1
            if end >= len(tokens):
                break
            start += step
        return chunks
