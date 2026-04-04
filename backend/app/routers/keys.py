import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_api_key, tenant_for_first_api_key
from app.db.session import get_db
from app.schemas.keys import ApiKeyCreate, ApiKeyCreated, ApiKeyOut
from app.services.api_key import create_api_key, list_api_keys, revoke_api_key

router = APIRouter(prefix="/v1/keys", tags=["keys"])


@router.post("", response_model=ApiKeyCreated, status_code=status.HTTP_201_CREATED)
async def create_key(
    body: ApiKeyCreate,
    tenant_id: Annotated[uuid.UUID, Depends(tenant_for_first_api_key)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ApiKeyCreated:
    row, raw = await create_api_key(session, tenant_id, body.scopes)
    return ApiKeyCreated(
        id=row.id,
        key=raw,
        key_prefix=row.key_prefix,
        scopes=list(row.scopes),
        created_at=row.created_at,
    )


@router.get("", response_model=list[ApiKeyOut])
async def list_keys(
    tenant_id: Annotated[uuid.UUID, Depends(require_api_key)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[ApiKeyOut]:
    rows = await list_api_keys(session, tenant_id)
    return [ApiKeyOut.model_validate(r) for r in rows]


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_key(
    key_id: uuid.UUID,
    tenant_id: Annotated[uuid.UUID, Depends(require_api_key)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    ok = await revoke_api_key(session, tenant_id, key_id)
    if not ok:
        raise HTTPException(status_code=404, detail="API key not found")
