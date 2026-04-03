from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)
    include_metadata: bool = True


class QueryResultItem(BaseModel):
    text: str
    score: float
    metadata: dict


class QueryResponse(BaseModel):
    results: list[QueryResultItem]
    latency_ms: int


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    top_k: int = Field(default=5, ge=1, le=50)


class ChatSource(BaseModel):
    filename: str | None
    excerpt: str
    chunk_index: int | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]
