import logging
import os
from collections.abc import AsyncGenerator

from sqlalchemy import Connection, inspect, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

logger = logging.getLogger("luminalearn.database")

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SQLITE_URI = f"sqlite+aiosqlite:///{os.path.join(_BACKEND_DIR, 'luminalearn.db').replace(os.sep, '/')}"

# Determine DB URI with SQLite fallback for local dev environment
use_sqlite = os.environ.get("USE_SQLITE", "true").lower() == "true"
db_uri = SQLITE_URI if use_sqlite else settings.ASYNC_DATABASE_URI


# Create Async SQLAlchemy Engine
engine: AsyncEngine = create_async_engine(
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

# Columns added after their table was first created. `create_all` never alters an
# existing table, so these are applied additively on startup.
_ADDITIVE_COLUMNS: dict[str, list[tuple[str, str]]] = {
    "users": [("is_verified", "BOOLEAN NOT NULL DEFAULT {false}")],
    "quiz_questions": [
        ("question_type", "VARCHAR(50) NOT NULL DEFAULT 'multiple_choice'"),
        ("source_reference", "VARCHAR(255)"),
    ],
}


def _apply_additive_migrations(sync_conn: Connection) -> None:
    """Adds any missing late-introduced columns using dialect-neutral schema inspection."""
    inspector = inspect(sync_conn)
    false_literal = "0" if sync_conn.dialect.name == "sqlite" else "FALSE"
    for table, columns in _ADDITIVE_COLUMNS.items():
        if not inspector.has_table(table):
            continue
        existing = {column["name"] for column in inspector.get_columns(table)}
        for name, ddl in columns:
            if name not in existing:
                sync_conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl.format(false=false_literal)}"))
                logger.info("Migrated %s: added column %s.", table, name)


async def _fall_back_to_sqlite(reason: Exception) -> None:
    """Rebinds every session to the embedded SQLite database (development resilience)."""
    global engine
    logger.warning("PostgreSQL unreachable (%s). Falling back to embedded SQLite at %s.", reason, SQLITE_URI)
    await engine.dispose()
    engine = create_async_engine(SQLITE_URI, echo=settings.DEBUG, future=True)
    AsyncSessionLocal.configure(bind=engine)


async def init_db() -> None:
    """Initialize database tables automatically on startup with safe column migrations."""
    import app.models  # noqa: F401 - ensure all ORM models are registered
    from app.models.user import Base

    if not use_sqlite:
        try:
            async with engine.connect() as probe:
                await probe.execute(text("SELECT 1"))
        except (OSError, TimeoutError, DBAPIError) as exc:
            # Production must fail fast: silently splitting writes across two databases loses data.
            if settings.ENVIRONMENT == "production":
                raise
            await _fall_back_to_sqlite(exc)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_apply_additive_migrations)


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
