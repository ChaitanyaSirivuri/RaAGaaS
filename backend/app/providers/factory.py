from app.chunking.base import ChunkingStrategy
from app.chunking.fixed import FixedChunker
from app.chunking.recursive import RecursiveChunker
from app.chunking.semantic import SemanticChunker
from app.core.config import Settings
from app.providers.base import EmbeddingProvider, VectorProvider
from app.providers.embedding.local import LocalEmbedding
from app.providers.embedding.openai import OpenAIEmbedding
from app.providers.vector.chroma import ChromaProvider
from app.providers.vector.pinecone import PineconeProvider
from app.providers.vector.weaviate import WeaviateProvider


def build_vector_provider(settings: Settings) -> VectorProvider:
    key = settings.vector_provider.lower().strip()
    if key == "weaviate":
        return WeaviateProvider(settings.weaviate_url)
    if key == "chroma":
        return ChromaProvider()
    if key == "pinecone":
        return PineconeProvider()
    return WeaviateProvider(settings.weaviate_url)


def build_embedding_provider(settings: Settings) -> EmbeddingProvider:
    key = settings.embedding_provider.lower().strip()
    if key == "openai":
        return OpenAIEmbedding(api_key=settings.openai_api_key, model=settings.embedding_model)
    if key == "local":
        return LocalEmbedding()
    return OpenAIEmbedding(api_key=settings.openai_api_key, model=settings.embedding_model)


def build_chunking_strategy(strategy_name: str) -> ChunkingStrategy:
    n = strategy_name.lower().strip()
    if n == "recursive":
        return RecursiveChunker()
    if n == "semantic":
        return SemanticChunker()
    return FixedChunker()
