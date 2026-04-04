import uuid
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_api_key
from app.db.session import get_db
from app.models.db import Collection, DbImportJob, DbSource
from app.models.enums import DbSourceStatus, ImportJobStatus
from app.schemas.db_import import (
    DbSchemaResponse,
    DbSourceOut,
    ImportJobOut,
    ImportStartRequest,
)
from app.services.db_migrator import (
    create_engine_for_uri,
    introspect_schema,
    save_uploaded_sqlite_file,
    selections_to_store,
)
from app.services.db_migrator import run_import_job as run_job

router = APIRouter(prefix="/v1/db-sources", tags=["db-import"])


@router.post("", response_model=DbSourceOut, status_code=status.HTTP_201_CREATED)
async def register_source(
    tenant_id: Annotated[uuid.UUID, Depends(require_api_key)],
    session: Annotated[AsyncSession, Depends(get_db)],
    label: str = Form(...),
    connection_uri: str | None = Form(None),
    file: UploadFile | None = File(None),
) -> DbSource:
    uri = connection_uri
    db_type = "unknown"
    if file is not None and file.filename:
        suffix = file.filename.lower()
        if suffix.endswith((".db", ".sqlite", ".sqlite3")):
            raw = await file.read()
            uri = save_uploaded_sqlite_file(raw)
            db_type = "sqlite"
    if uri is None or not uri.strip():
        raise HTTPException(status_code=400, detail="connection_uri or sqlite file required")
    if db_type == "unknown":
        if "postgresql" in uri:
            db_type = "postgres"
        elif "mysql" in uri:
            db_type = "mysql"
        elif "sqlite" in uri:
            db_type = "sqlite"
    row = DbSource(
        tenant_id=tenant_id,
        label=label,
        db_type=db_type,
        connection_uri=uri,
        status=DbSourceStatus.connected,
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


@router.get("/{source_id}/schema", response_model=DbSchemaResponse)
async def get_schema(
    source_id: uuid.UUID,
    tenant_id: Annotated[uuid.UUID, Depends(require_api_key)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> DbSchemaResponse:
    res = await session.execute(
        select(DbSource).where(DbSource.id == source_id, DbSource.tenant_id == tenant_id),
    )
    src = res.scalar_one_or_none()
    if src is None:
        raise HTTPException(status_code=404, detail="Source not found")
    engine = await create_engine_for_uri(src.connection_uri)
    try:
        tables = await introspect_schema(engine)
    finally:
        await engine.dispose()
    return DbSchemaResponse(tables=tables)


async def _import_bg(job_id: uuid.UUID) -> None:
    from app.core.config import get_settings
    from app.db.session import async_session_maker
    from app.providers.factory import build_embedding_provider, build_vector_provider

    settings = get_settings()
    vector = build_vector_provider(settings)
    embedder = build_embedding_provider(settings)
    maker = async_session_maker()
    async with maker() as s:
        await run_job(s, job_id, vector, embedder)
    close = getattr(vector, "close", None)
    if callable(close):
        await close()


@router.post(
    "/{source_id}/import", response_model=ImportJobOut, status_code=status.HTTP_201_CREATED
)
async def start_import(
    source_id: uuid.UUID,
    body: ImportStartRequest,
    background_tasks: BackgroundTasks,
    tenant_id: Annotated[uuid.UUID, Depends(require_api_key)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> DbImportJob:
    res = await session.execute(
        select(DbSource).where(DbSource.id == source_id, DbSource.tenant_id == tenant_id),
    )
    if res.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Source not found")
    col_res = await session.execute(
        select(Collection).where(
            Collection.id == body.collection_id,
            Collection.tenant_id == tenant_id,
        ),
    )
    if col_res.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Collection not found")

    job = DbImportJob(
        source_id=source_id,
        collection_id=body.collection_id,
        selected_columns=selections_to_store(body.selections),
        status=ImportJobStatus.pending,
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)
    background_tasks.add_task(_import_bg, job.id)
    return job


@router.get("/{source_id}/import/{job_id}", response_model=ImportJobOut)
async def get_job(
    source_id: uuid.UUID,
    job_id: uuid.UUID,
    tenant_id: Annotated[uuid.UUID, Depends(require_api_key)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> DbImportJob:
    res = await session.execute(
        select(DbImportJob).where(
            DbImportJob.id == job_id,
            DbImportJob.source_id == source_id,
        ),
    )
    job = res.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    sres = await session.execute(select(DbSource).where(DbSource.id == source_id))
    src = sres.scalar_one_or_none()
    if src is None or src.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
