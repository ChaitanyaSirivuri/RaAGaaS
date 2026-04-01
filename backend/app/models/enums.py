from enum import StrEnum


class DocumentStatus(StrEnum):
    pending = "pending"
    processing = "processing"
    done = "done"
    error = "error"


class DbSourceStatus(StrEnum):
    connected = "connected"
    error = "error"


class ImportJobStatus(StrEnum):
    pending = "pending"
    running = "running"
    done = "done"
    error = "error"
