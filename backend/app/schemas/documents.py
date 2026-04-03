import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import DocumentStatus


class DocumentOut(BaseModel):
    id: uuid.UUID
    collection_id: uuid.UUID
    filename: str
    status: DocumentStatus
    chunk_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
