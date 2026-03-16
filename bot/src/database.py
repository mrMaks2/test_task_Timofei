from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .models import Base

engine = None
async_session_maker = None

async def init_db():
    global engine, async_session_maker
    from .config import settings
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    # Создание таблиц (для разработки; в проде используйте миграции Django)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    if engine:
        await engine.dispose()

async def get_session() -> AsyncSession: # type: ignore
    async with async_session_maker() as session:
        yield session