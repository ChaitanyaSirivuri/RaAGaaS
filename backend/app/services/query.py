import time
from typing import Any

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import Collection
from app.providers.base import EmbeddingProvider, VectorProvider


class QueryService:
    def __init__(
        self,
        vector: VectorProvider,
        embedder: EmbeddingProvider,
        openai_client: AsyncOpenAI | None = None,
    ) -> None:
        self._vector = vector
        self._embedder = embedder
        self._openai = openai_client

    async def query(
        self,
        session: AsyncSession,
        collection: Collection,
        query_text: str,
        top_k: int,
        include_metadata: bool,
    ) -> tuple[list[dict[str, Any]], int]:
        _ = session
        _ = include_metadata
        t0 = time.perf_counter()
        qv = (await self._embedder.embed([query_text]))[0]
        hits = await self._vector.search(collection.weaviate_class, qv, top_k)
        latency_ms = int((time.perf_counter() - t0) * 1000)
        results = [
            {
                "text": h.text,
                "score": h.score,
                "metadata": h.metadata,
            }
            for h in hits
        ]
        return results, latency_ms

    async def chat(
        self,
        session: AsyncSession,
        collection: Collection,
        messages: list[dict[str, str]],
        top_k: int,
    ) -> tuple[str, list[dict[str, Any]]]:
        _ = session
        if not messages:
            return "No messages provided.", []
        last_user = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
        if not last_user.strip():
            return "No user message to answer.", []
        qv = (await self._embedder.embed([last_user]))[0]
        hits = await self._vector.search(collection.weaviate_class, qv, top_k)
        context_blocks = []
        sources: list[dict[str, Any]] = []
        for h in hits:
            fn = h.metadata.get("filename") if h.metadata else None
            excerpt = h.text[:500] + ("…" if len(h.text) > 500 else "")
            context_blocks.append(f"Source ({fn}):\n{h.text}")
            sources.append(
                {
                    "filename": fn,
                    "excerpt": excerpt,
                    "chunk_index": (h.metadata or {}).get("chunk_index"),
                },
            )
        context = "\n\n---\n\n".join(context_blocks)
        if self._openai is None:
            return (
                "OpenAI client not configured; here are the top retrieved passages.",
                sources,
            )
        system = (
            "You are a helpful assistant. Answer using only the provided context. "
            "If the answer is not in the context, say you do not know."
        )
        user = f"Context:\n{context}\n\nQuestion:\n{last_user}"
        resp = await self._openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
        )
        answer = resp.choices[0].message.content or ""
        return answer, sources
