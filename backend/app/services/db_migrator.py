from __future__ import annotations

import json
import tempfile
import uuid
from pathlib import Path
from typing import Any

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from app.models.db import Collection, DbImportJob, DbSource
from app.models.enums import ImportJobStatus
from app.providers.base import EmbeddingProvider, VectorProvider, VectorUpsert
from app.schemas.db_import import ColumnInfo, TableSchema


def normalize_async_database_url(uri: str) -> str:
    u = uri.strip()
    if u.startswith("postgresql://"):
        return u.replace("postgresql://", "postgresql+asyncpg://", 1)
    if u.startswith("mysql://"):
        return u.replace("mysql://", "mysql+aiomysql://", 1)
    if u.startswith("sqlite://"):
        return u.replace("sqlite://", "sqlite+aiosqlite://", 1)
    return u


async def create_engine_for_uri(uri: str) -> AsyncEngine:
    return create_async_engine(normalize_async_database_url(uri), echo=False)


async def introspect_schema(engine: AsyncEngine) -> list[TableSchema]:
    async with engine.connect() as conn:

        def _inspect(sync_conn: Any) -> Any:
            return inspect(sync_conn)

        insp = await conn.run_sync(_inspect)
        tables: list[TableSchema] = []
        for name in insp.get_table_names():
            cols: list[ColumnInfo] = []
            for col in insp.get_columns(name):
                cols.append(ColumnInfo(name=col["name"], type=str(col["type"])))
            tables.append(TableSchema(name=name, columns=cols))
        return tables


def save_uploaded_sqlite_file(content: bytes) -> str:
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    Path(path).write_bytes(content)
    return f"sqlite+aiosqlite:///{path.replace(chr(92), '/')}"


def selections_to_store(selections: list[Any]) -> dict[str, Any]:
    return {"selections": [s.model_dump() for s in selections]}


async def run_import_job(
    session: AsyncSession,
    job_id: uuid.UUID,
    vector: VectorProvider,
    embedder: EmbeddingProvider,
) -> None:
    res = await session.get(DbImportJob, job_id)
    if res is None:
        return
    job = res
    source = await session.get(DbSource, job.source_id)
    collection = await session.get(Collection, job.collection_id)
    if source is None or collection is None:
        job.status = ImportJobStatus.error
        await session.commit()
        return

    job.status = ImportJobStatus.running
    job.rows_processed = 0
    await session.commit()

    try:
        engine = await create_engine_for_uri(source.connection_uri)
        payload = job.selected_columns
        selections = payload.get("selections", [])
        await vector.create_collection(collection.weaviate_class, embedder.dim)

        rows_total = 0
        async with engine.connect() as conn:
            prep = conn.dialect.identifier_preparer
            for sel in selections:
                table = sel["table"]
                cols = [c["column"] for c in sel["columns"] if c.get("use_as_text")]
                meta_cols = [c["column"] for c in sel["columns"] if c.get("store_as_metadata")]
                if not cols:
                    continue
                all_cols = list(dict.fromkeys(cols + meta_cols))
                quoted_cols = ", ".join(prep.quote(c) for c in all_cols)
                qtable = prep.quote(table)
                offset = 0
                batch_size = 500
                while True:
                    stmt = text(f"SELECT {quoted_cols} FROM {qtable} LIMIT :lim OFFSET :off")
                    result = await conn.execute(stmt, {"lim": batch_size, "off": offset})
                    rows = result.mappings().all()
                    if not rows:
                        break
                    texts: list[str] = []
                    metas: list[dict[str, Any]] = []
                    for row in rows:
                        parts = [str(row[c]) for c in cols if row.get(c) is not None]
                        texts.append(" ".join(parts))
                        metas.append({m: row.get(m) for m in meta_cols})
                    embeddings = await embedder.embed(texts)
                    upserts: list[VectorUpsert] = []
                    for i, emb in enumerate(embeddings):
                        meta_json = json.dumps(metas[i], default=str) if metas[i] else "{}"
                        upserts.append(
                            VectorUpsert(
                                uuid=str(uuid.uuid4()),
                                vector=emb,
                                properties={
                                    "text": texts[i],
                                    "doc_id": f"db:{table}:{offset + i}",
                                    "chunk_index": offset + i,
                                    "filename": f"{source.label}:{table}",
                                    "meta": meta_json,
                                },
                            ),
                        )
                    await vector.upsert(collection.weaviate_class, upserts)
                    rows_total += len(rows)
                    job.rows_processed = rows_total
                    await session.commit()
                    offset += batch_size

        job.status = ImportJobStatus.done
        await session.commit()
        await engine.dispose()
    except Exception:
        job.status = ImportJobStatus.error
        await session.commit()
        raise
