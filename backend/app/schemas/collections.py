import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CollectionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=512)
    embedding_model: str | None = None
    chunk_strategy: str = "fixed"
    chunk_size: int = Field(ge=32, le=8192, default=512)
    chunk_overlap: int = Field(ge=0, le=2048, default=64)


class CollectionOut(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    embedding_model: str
    chunk_strategy: str
    chunk_size: int
    chunk_overlap: int
    weaviate_class: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CollectionDetail(CollectionOut):
    document_count: int = 0
