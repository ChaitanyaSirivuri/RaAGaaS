import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import DbSourceStatus, ImportJobStatus


class DbSourceCreate(BaseModel):
    label: str = Field(min_length=1)
    connection_uri: str | None = None


class DbSourceOut(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    label: str
    db_type: str
    connection_uri: str
    status: DbSourceStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class ColumnInfo(BaseModel):
    name: str
    type: str


class TableSchema(BaseModel):
    name: str
    columns: list[ColumnInfo]


class DbSchemaResponse(BaseModel):
    tables: list[TableSchema]


class ColumnMapping(BaseModel):
    column: str
    use_as_text: bool = True
    store_as_metadata: bool = False


class TableColumnSelection(BaseModel):
    table: str
    columns: list[ColumnMapping]


class ImportStartRequest(BaseModel):
    collection_id: uuid.UUID
    selections: list[TableColumnSelection]


class ImportJobOut(BaseModel):
    id: uuid.UUID
    source_id: uuid.UUID
    collection_id: uuid.UUID
    selected_columns: dict[str, Any]
    status: ImportJobStatus
    rows_processed: int
    created_at: datetime

    model_config = {"from_attributes": True}
