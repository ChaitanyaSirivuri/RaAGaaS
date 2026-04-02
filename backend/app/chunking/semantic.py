from app.chunking.base import Chunk, ChunkConfig, ChunkingStrategy


class SemanticChunker(ChunkingStrategy):
    def chunk(self, text: str, config: ChunkConfig) -> list[Chunk]:
        raise NotImplementedError("SemanticChunker is a stub for v2")
