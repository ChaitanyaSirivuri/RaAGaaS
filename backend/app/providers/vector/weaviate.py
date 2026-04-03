from __future__ import annotations

import uuid
from typing import TYPE_CHECKING
from urllib.parse import urlparse

import weaviate
from weaviate.classes.config import Configure, DataType, Property
from weaviate.classes.query import MetadataQuery

from app.providers.base import SearchResult, VectorProvider, VectorUpsert

if TYPE_CHECKING:
    from weaviate.client import WeaviateAsyncClient


def _parse_weaviate_url(url: str) -> tuple[str, int, bool, str, int, bool]:
    parsed = urlparse(url)
    host = parsed.hostname or "localhost"
    port = parsed.port or (443 if parsed.scheme == "https" else 8080)
    secure = parsed.scheme == "https"
    grpc_host = host
    grpc_port = 50051
    grpc_secure = secure
    return host, port, secure, grpc_host, grpc_port, grpc_secure


class WeaviateProvider(VectorProvider):
    """Weaviate v4 async client behind :class:`VectorProvider`."""

    def __init__(self, weaviate_url: str) -> None:
        self._weaviate_url = weaviate_url
        self._client: WeaviateAsyncClient | None = None

    async def _get_client(self) -> WeaviateAsyncClient:
        if self._client is None:
            http_host, http_port, http_secure, grpc_host, grpc_port, grpc_secure = (
                _parse_weaviate_url(self._weaviate_url)
            )
            self._client = weaviate.use_async_with_custom(
                http_host=http_host,
                http_port=http_port,
                http_secure=http_secure,
                grpc_host=grpc_host,
                grpc_port=grpc_port,
                grpc_secure=grpc_secure,
            )
            await self._client.connect()
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.close()
            self._client = None

    async def create_collection(self, name: str, dim: int) -> None:
        _ = dim  # inferred on first upsert for self_provided vectors
        client = await self._get_client()
        if await client.collections.exists(name):
            return
        await client.collections.create(
            name=name,
            vector_config=Configure.Vectors.self_provided(),
            properties=[
                Property(name="text", data_type=DataType.TEXT),
                Property(name="doc_id", data_type=DataType.TEXT),
                Property(name="chunk_index", data_type=DataType.INT),
                Property(name="filename", data_type=DataType.TEXT),
                Property(name="meta", data_type=DataType.TEXT),
            ],
        )

    async def upsert(self, collection: str, vectors: list[VectorUpsert]) -> None:
        if not vectors:
            return
        client = await self._get_client()
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            chunk = vectors[i : i + batch_size]
            async with client.batch.fixed_size(batch_size=len(chunk)) as batch:
                for row in chunk:
                    uid = row.uuid if isinstance(row.uuid, uuid.UUID) else uuid.UUID(row.uuid)
                    await batch.add_object(
                        collection=collection,
                        uuid=uid,
                        vector=row.vector,
                        properties=row.properties,
                    )

    async def search(
        self, collection: str, query_vec: list[float], top_k: int
    ) -> list[SearchResult]:
        client = await self._get_client()
        coll = client.collections.get(collection)
        response = await coll.query.near_vector(
            near_vector=query_vec,
            limit=top_k,
            return_properties=["text", "doc_id", "chunk_index", "filename", "meta"],
            return_metadata=MetadataQuery(distance=True),
        )
        results: list[SearchResult] = []
        for obj in response.objects:
            props = obj.properties or {}
            dist = None
            if obj.metadata and obj.metadata.distance is not None:
                dist = float(obj.metadata.distance)
            score = 1.0 / (1.0 + dist) if dist is not None else 0.0
            results.append(
                SearchResult(
                    text=str(props.get("text", "")),
                    score=score,
                    metadata={
                        "doc_id": props.get("doc_id"),
                        "chunk_index": props.get("chunk_index"),
                        "filename": props.get("filename"),
                        "distance": dist,
                    },
                )
            )
        return results

    async def delete_collection(self, name: str) -> None:
        client = await self._get_client()
        if await client.collections.exists(name):
            await client.collections.delete(name)
