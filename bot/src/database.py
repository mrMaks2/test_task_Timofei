from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

engine: Optional[object] = None
async_session_maker: Optional[async_sessionmaker[AsyncSession]] = None


async def init_db() -> None:
    global engine, async_session_maker
    from .config import settings
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def close_db() -> None:
    if engine:
        await engine.dispose()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if not async_session_maker:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    async with async_session_maker() as session:
        yield session
