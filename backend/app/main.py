from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import AsyncOpenAI

from app.core.config import get_settings
from app.db.session import async_session_maker
from app.providers.factory import build_embedding_provider, build_vector_provider
from app.routers import collections, db_import, documents, keys, query
from app.services.api_key import ensure_default_tenant
from app.services.query import QueryService


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.vector = build_vector_provider(settings)
    app.state.embedder = build_embedding_provider(settings)
    oa = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
    app.state.query_service = QueryService(app.state.vector, app.state.embedder, oa)
    maker = async_session_maker()
    async with maker() as session:
        await ensure_default_tenant(session)
    yield
    close = getattr(app.state.vector, "close", None)
    if callable(close):
        await close()


app = FastAPI(title="RaaGaaS", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.exception_handler(HTTPException)
async def http_exc_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(collections.router)
app.include_router(documents.router)
app.include_router(query.router)
app.include_router(keys.router)
app.include_router(db_import.router)
