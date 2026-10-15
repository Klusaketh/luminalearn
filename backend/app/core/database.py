import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# Determine DB URI with SQLite fallback for local dev environment
db_uri = settings.ASYNC_DATABASE_URI
if os.environ.get("USE_SQLITE", "true").lower() == "true":
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    db_file = os.path.join(backend_dir, "luminalearn.db")
    db_uri = f"sqlite+aiosqlite:///{db_file.replace(os.sep, '/')}"


# Create Async SQLAlchemy Engine
engine = create_async_engine(
    db_uri,
    echo=settings.DEBUG,
    future=True,
)

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Alias for backward compatibility & dependency injection
async_session_factory = AsyncSessionLocal


async def init_db() -> None:
    """Initialize database tables automatically on startup with safe column migrations."""
    from sqlalchemy import text
    from app.models.user import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Safe migration for is_verified column
        try:
            check_sql = text("PRAGMA table_info(users)")
            result = await conn.execute(check_sql)
            columns = [row[1] for row in result.fetchall()]
            if columns and "is_verified" not in columns:
                await conn.execute(text("ALTER TABLE users ADD COLUMN is_verified BOOLEAN NOT NULL DEFAULT 0"))
        except Exception:
            try:
                await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN NOT NULL DEFAULT FALSE"))
            except Exception:
                pass


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI Dependency yielding Async Database Sessions.
    Automatically handles session closing and rollback on exceptions.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

