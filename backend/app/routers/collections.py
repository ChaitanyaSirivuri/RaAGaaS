import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.deps import api_settings, get_embedding_provider, get_vector_provider, require_api_key
from app.db.session import get_db
from app.models.db import Collection, Document
from app.providers.base import EmbeddingProvider, VectorProvider
from app.schemas.collections import CollectionCreate, CollectionDetail, CollectionOut

router = APIRouter(prefix="/v1/collections", tags=["collections"])


@router.post("", response_model=CollectionOut, status_code=status.HTTP_201_CREATED)
async def create_collection(
    body: CollectionCreate,
    tenant_id: Annotated[uuid.UUID, Depends(require_api_key)],
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(api_settings)],
    vector: Annotated[VectorProvider, Depends(get_vector_provider)],
    embedder: Annotated[EmbeddingProvider, Depends(get_embedding_provider)],
) -> Collection:
    cid = uuid.uuid4()
    weaviate_class = f"Collection_{cid.hex}"
    model = body.embedding_model or settings.embedding_model
    col = Collection(
        id=cid,
        tenant_id=tenant_id,
        name=body.name,
        embedding_model=model,
        chunk_strategy=body.chunk_strategy,
        chunk_size=body.chunk_size,
        chunk_overlap=body.chunk_overlap,
        weaviate_class=weaviate_class,
    )
    session.add(col)
    await session.flush()
    await vector.create_collection(weaviate_class, embedder.dim)
    await session.commit()
    await session.refresh(col)
    return col


@router.get("", response_model=list[CollectionOut])
async def list_collections(
    tenant_id: Annotated[uuid.UUID, Depends(require_api_key)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[Collection]:
    res = await session.execute(
        select(Collection)
        .where(Collection.tenant_id == tenant_id)
        .order_by(Collection.created_at.desc()),
    )
    return list(res.scalars().all())


@router.get("/{collection_id}", response_model=CollectionDetail)
async def get_collection(
    collection_id: uuid.UUID,
    tenant_id: Annotated[uuid.UUID, Depends(require_api_key)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CollectionDetail:
    res = await session.execute(
        select(Collection).where(Collection.id == collection_id, Collection.tenant_id == tenant_id),
    )
    col = res.scalar_one_or_none()
    if col is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    cnt = await session.scalar(
        select(func.count()).select_from(Document).where(Document.collection_id == collection_id),
    )
    return CollectionDetail(
        id=col.id,
        tenant_id=col.tenant_id,
        name=col.name,
        embedding_model=col.embedding_model,
        chunk_strategy=col.chunk_strategy,
        chunk_size=col.chunk_size,
        chunk_overlap=col.chunk_overlap,
        weaviate_class=col.weaviate_class,
        created_at=col.created_at,
        document_count=int(cnt or 0),
    )


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    collection_id: uuid.UUID,
    tenant_id: Annotated[uuid.UUID, Depends(require_api_key)],
    session: Annotated[AsyncSession, Depends(get_db)],
    vector: Annotated[VectorProvider, Depends(get_vector_provider)],
) -> None:
    res = await session.execute(
        select(Collection).where(Collection.id == collection_id, Collection.tenant_id == tenant_id),
    )
    col = res.scalar_one_or_none()
    if col is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    wc = col.weaviate_class
    await session.delete(col)
    await session.commit()
    await vector.delete_collection(wc)
