import io
import uuid

import pandas as pd
from docx import Document as DocxDocument
from pypdf import PdfReader
from sqlalchemy.ext.asyncio import AsyncSession

from app.chunking.base import ChunkConfig
from app.models.db import Collection, Document
from app.models.enums import DocumentStatus
from app.providers.base import EmbeddingProvider, VectorProvider, VectorUpsert
from app.providers.factory import build_chunking_strategy


def _extract_text(file_bytes: bytes, content_type: str, filename: str) -> str:
    ct = (content_type or "").lower()
    fn = filename.lower()

    if "pdf" in ct or fn.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_bytes))
        parts: list[str] = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                parts.append(t)
        return "\n".join(parts)

    if "wordprocessingml" in ct or "msword" in ct or fn.endswith(".docx"):
        doc = DocxDocument(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs if p.text)

    if "csv" in ct or fn.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(file_bytes))
        return df.astype(str).to_csv(index=False)

    if "markdown" in ct or fn.endswith(".md") or "text/plain" in ct or fn.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="replace")

    return file_bytes.decode("utf-8", errors="replace")


async def ingest_document_bytes(
    session: AsyncSession,
    vector: VectorProvider,
    embedder: EmbeddingProvider,
    collection: Collection,
    document: Document,
    file_bytes: bytes,
    content_type: str,
) -> None:
    document.status = DocumentStatus.processing
    await session.flush()

    try:
        text = _extract_text(file_bytes, content_type, document.filename)
        strategy = build_chunking_strategy(collection.chunk_strategy)
        config = ChunkConfig(
            strategy=collection.chunk_strategy,
            size=collection.chunk_size,
            overlap=collection.chunk_overlap,
        )
        chunks = strategy.chunk(text, config)
        if not chunks:
            document.status = DocumentStatus.done
            document.chunk_count = 0
            await session.commit()
            return

        weaviate_class = collection.weaviate_class
        await vector.create_collection(weaviate_class, embedder.dim)

        batch_size = 100
        total = 0
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            texts = [c.text for c in batch]
            embeddings = await embedder.embed(texts)
            upserts: list[VectorUpsert] = []
            for j, ch in enumerate(batch):
                upserts.append(
                    VectorUpsert(
                        uuid=str(uuid.uuid4()),
                        vector=embeddings[j],
                        properties={
                            "text": ch.text,
                            "doc_id": str(document.id),
                            "chunk_index": ch.index,
                            "filename": document.filename,
                            "meta": "",
                        },
                    ),
                )
            await vector.upsert(weaviate_class, upserts)
            total += len(batch)

        document.chunk_count = total
        document.status = DocumentStatus.done
        await session.commit()
    except Exception:
        document.status = DocumentStatus.error
        await session.commit()
        raise
