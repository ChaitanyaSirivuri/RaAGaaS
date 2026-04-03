from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _ensure_engine() -> None:
    global _engine, _session_factory
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(settings.database_url, echo=False)
        _session_factory = async_sessionmaker(_engine, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    _ensure_engine()
    assert _session_factory is not None
    async with _session_factory() as session:
        yield session


def async_session_maker() -> async_sessionmaker[AsyncSession]:
    _ensure_engine()
    assert _session_factory is not None
    return _session_factory
