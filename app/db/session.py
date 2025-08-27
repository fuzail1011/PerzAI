from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import Settings

Settings()
# Async SQLAlchemy engine
engine = create_async_engine(
    Settings.DATABASE_URL,
    echo=True,
    future=True,
)

# Async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# Dependency for FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
