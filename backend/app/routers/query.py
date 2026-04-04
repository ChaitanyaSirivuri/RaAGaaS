import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_query_service, require_api_key
from app.db.session import get_db
from app.models.db import Collection
from app.schemas.query import (
    ChatRequest,
    ChatResponse,
    ChatSource,
    QueryRequest,
    QueryResponse,
    QueryResultItem,
)
from app.services.query import QueryService

router = APIRouter(prefix="/v1/collections", tags=["query"])


@router.post("/{collection_id}/query", response_model=QueryResponse)
async def run_query(
    collection_id: uuid.UUID,
    body: QueryRequest,
    tenant_id: Annotated[uuid.UUID, Depends(require_api_key)],
    session: Annotated[AsyncSession, Depends(get_db)],
    qsvc: Annotated[QueryService, Depends(get_query_service)],
) -> QueryResponse:
    res = await session.execute(
        select(Collection).where(Collection.id == collection_id, Collection.tenant_id == tenant_id),
    )
    col = res.scalar_one_or_none()
    if col is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    results, latency_ms = await qsvc.query(
        session, col, body.query, body.top_k, body.include_metadata
    )
    return QueryResponse(
        results=[QueryResultItem(**r) for r in results],
        latency_ms=latency_ms,
    )


@router.post("/{collection_id}/chat", response_model=ChatResponse)
async def run_chat(
    collection_id: uuid.UUID,
    body: ChatRequest,
    tenant_id: Annotated[uuid.UUID, Depends(require_api_key)],
    session: Annotated[AsyncSession, Depends(get_db)],
    qsvc: Annotated[QueryService, Depends(get_query_service)],
) -> ChatResponse:
    res = await session.execute(
        select(Collection).where(Collection.id == collection_id, Collection.tenant_id == tenant_id),
    )
    col = res.scalar_one_or_none()
    if col is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    msgs = [{"role": m.role, "content": m.content} for m in body.messages]
    answer, sources = await qsvc.chat(session, col, msgs, body.top_k)
    return ChatResponse(
        answer=answer,
        sources=[ChatSource(**s) for s in sources],
    )
