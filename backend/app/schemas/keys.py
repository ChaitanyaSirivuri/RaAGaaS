import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ApiKeyCreate(BaseModel):
    scopes: list[str] = Field(default_factory=lambda: ["query", "ingest"])


class ApiKeyCreated(BaseModel):
    id: uuid.UUID
    key: str
    key_prefix: str
    scopes: list[str]
    created_at: datetime


class ApiKeyOut(BaseModel):
    id: uuid.UUID
    key_prefix: str
    scopes: list[str]
    expires_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
