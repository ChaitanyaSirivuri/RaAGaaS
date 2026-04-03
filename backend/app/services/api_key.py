import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    api_key_lookup_prefix,
    generate_api_key_raw,
    hash_api_key,
    verify_api_key,
)
from app.models.db import ApiKey, Tenant


async def create_api_key(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    scopes: list[str],
) -> tuple[ApiKey, str]:
    raw = generate_api_key_raw()
    prefix = api_key_lookup_prefix(raw, 8)
    row = ApiKey(
        tenant_id=tenant_id,
        key_prefix=prefix,
        key_hash=hash_api_key(raw),
        scopes=scopes,
    )
    session.add(row)
    await session.flush()
    await session.refresh(row)
    await session.commit()
    return row, raw


async def list_api_keys(session: AsyncSession, tenant_id: uuid.UUID) -> list[ApiKey]:
    res = await session.execute(
        select(ApiKey).where(ApiKey.tenant_id == tenant_id).order_by(ApiKey.created_at.desc()),
    )
    return list(res.scalars().all())


async def revoke_api_key(session: AsyncSession, tenant_id: uuid.UUID, key_id: uuid.UUID) -> bool:
    res = await session.execute(
        select(ApiKey).where(ApiKey.id == key_id, ApiKey.tenant_id == tenant_id),
    )
    row = res.scalar_one_or_none()
    if row is None:
        return False
    await session.delete(row)
    await session.commit()
    return True


async def resolve_tenant_from_api_key(session: AsyncSession, raw_key: str) -> uuid.UUID | None:
    prefix = api_key_lookup_prefix(raw_key, 8)
    if not prefix:
        return None
    res = await session.execute(select(ApiKey).where(ApiKey.key_prefix == prefix))
    candidates = list(res.scalars().all())
    for key in candidates:
        if verify_api_key(raw_key, key.key_hash):
            return key.tenant_id
    return None


async def ensure_default_tenant(session: AsyncSession) -> Tenant:
    res = await session.execute(select(Tenant).order_by(Tenant.created_at.asc()).limit(1))
    row = res.scalar_one_or_none()
    if row:
        return row
    t = Tenant(name="default")
    session.add(t)
    await session.commit()
    await session.refresh(t)
    return t
