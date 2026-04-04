from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.models.db import ApiKey, Collection
from app.providers.base import EmbeddingProvider, VectorProvider
from app.services.api_key import ensure_default_tenant, resolve_tenant_from_api_key
from app.services.query import QueryService


async def api_settings() -> Settings:
    return get_settings()


async def db_session(session: Annotated[AsyncSession, Depends(get_db)]) -> AsyncSession:
    return session


def get_vector_provider(request: Request) -> VectorProvider:
    return request.app.state.vector


def get_embedding_provider(request: Request) -> EmbeddingProvider:
    return request.app.state.embedder


def get_query_service(request: Request) -> QueryService:
    return request.app.state.query_service


async def tenant_for_first_api_key(
    session: Annotated[AsyncSession, Depends(get_db)],
    authorization: Annotated[str | None, Header()] = None,
) -> UUID:
    """Allow unauthenticated creation of the very first API key (binds to default tenant)."""
    n = await session.scalar(select(func.count()).select_from(ApiKey))
    if n == 0:
        t = await ensure_default_tenant(session)
        return t.id
    return await require_api_key(session, authorization)


async def require_api_key(
    session: Annotated[AsyncSession, Depends(get_db)],
    authorization: Annotated[str | None, Header()] = None,
) -> UUID:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    raw = authorization.split(" ", 1)[1].strip()
    tenant_id = await resolve_tenant_from_api_key(session, raw)
    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return tenant_id


async def get_collection_for_tenant(
    collection_id: UUID,
    tenant_id: Annotated[UUID, Depends(require_api_key)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> Collection:
    res = await session.execute(
        select(Collection).where(Collection.id == collection_id, Collection.tenant_id == tenant_id),
    )
    row = res.scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    return row
