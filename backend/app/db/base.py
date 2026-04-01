from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase

from app.models.enums import DbSourceStatus, DocumentStatus, ImportJobStatus


class Base(DeclarativeBase):
    type_annotation_map = {
        DocumentStatus: String(32),
        DbSourceStatus: String(32),
        ImportJobStatus: String(32),
    }
