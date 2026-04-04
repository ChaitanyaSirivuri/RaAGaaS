import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_api_key
from app.db.session import get_db
from app.models.db import Collection, Document
from app.models.enums import DocumentStatus
from app.schemas.documents import DocumentOut
from app.services.ingestion import ingest_document_bytes

router = APIRouter(prefix="/v1/collections", tags=["documents"])


async def _ingest_task(
    document_id: uuid.UUID,
    collection_id: uuid.UUID,
    file_bytes: bytes,
    content_type: str,
) -> None:
    from app.core.config import get_settings
    from app.db.session import async_session_maker
    from app.providers.factory import build_embedding_provider, build_vector_provider

    settings = get_settings()
    vector = build_vector_provider(settings)
    embedder = build_embedding_provider(settings)
    maker = async_session_maker()
    async with maker() as session:
        col = await session.get(Collection, collection_id)
        doc = await session.get(Document, document_id)
        if col is None or doc is None:
            return
        await ingest_document_bytes(session, vector, embedder, col, doc, file_bytes, content_type)
    if hasattr(vector, "close"):
        c = vector.close
        if callable(c):
            await c()


@router.post(
    "/{collection_id}/documents", response_model=DocumentOut, status_code=status.HTTP_201_CREATED
)
async def upload_document(
    collection_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    tenant_id: Annotated[uuid.UUID, Depends(require_api_key)],
    session: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...),
) -> Document:
    res = await session.execute(
        select(Collection).where(Collection.id == collection_id, Collection.tenant_id == tenant_id),
    )
    col = res.scalar_one_or_none()
    if col is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    raw = await file.read()
    doc = Document(
        collection_id=collection_id,
        filename=file.filename or "upload",
        status=DocumentStatus.pending,
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    ct = file.content_type or "application/octet-stream"
    background_tasks.add_task(_ingest_task, doc.id, collection_id, raw, ct)
    return doc


@router.get("/{collection_id}/documents", response_model=list[DocumentOut])
async def list_documents(
    collection_id: uuid.UUID,
    tenant_id: Annotated[uuid.UUID, Depends(require_api_key)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[Document]:
    res = await session.execute(
        select(Collection).where(Collection.id == collection_id, Collection.tenant_id == tenant_id),
    )
    if res.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    q = await session.execute(
        select(Document)
        .where(Document.collection_id == collection_id)
        .order_by(Document.created_at.desc()),
    )
    return list(q.scalars().all())


@router.delete("/{collection_id}/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    collection_id: uuid.UUID,
    doc_id: uuid.UUID,
    tenant_id: Annotated[uuid.UUID, Depends(require_api_key)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    res = await session.execute(
        select(Collection).where(Collection.id == collection_id, Collection.tenant_id == tenant_id),
    )
    if res.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    doc = await session.get(Document, doc_id)
    if doc is None or doc.collection_id != collection_id:
        raise HTTPException(status_code=404, detail="Document not found")
    await session.delete(doc)
    await session.commit()
