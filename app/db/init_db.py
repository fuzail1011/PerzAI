import psycopg
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import Settings
from app.models.user import User
from app.models.persona import Persona
from loguru import logger


def ensure_database() -> None:
    """
    Ensure the target database exists, create it if missing.
    Uses psycopg3 (sync) because CREATE DATABASE cannot be run inside an async transaction.
    """
    Settings.validate()

    db_name = Settings.DB_NAME
    logger.info(f"🔍 Checking if database '{db_name}' exists...")

    # Connect to the default 'postgres' DB to check/create our target DB
    base_url = (
        f"postgresql+psycopg://{Settings.DB_USER}:{Settings.DB_PASSWORD}"
        f"@{Settings.DB_HOST}:{Settings.DB_PORT}/postgres"
    )

    with psycopg.connect(base_url.replace("+psycopg", "")) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            if not cur.fetchone():
                cur.execute(f'CREATE DATABASE "{db_name}"')
                logger.success(f"✅ Database '{db_name}' created.")
            else:
                logger.info(f"ℹ️ Database '{db_name}' already exists.")


async def init_db_models() -> None:
    """
    Initialize all tables inside the target database.
    """
    Settings.validate()

    engine = create_async_engine(
        Settings.DATABASE_URL,
        echo=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(User.metadata.create_all)
        await conn.run_sync(Persona.metadata.create_all)

    await engine.dispose()
    logger.success("✅ Database tables ensured.")
