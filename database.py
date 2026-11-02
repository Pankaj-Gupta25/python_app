from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import os

# Load .env file automatically in local development
load_dotenv()

# Read the Neon DB connection string from environment.
# Strip the ?sslmode=require suffix if present — asyncpg handles SSL
# via connect_args, not as a query parameter.
_raw_url = os.environ.get("DATABASE_URL", "")
DATABASE_URL = _raw_url.replace("?sslmode=require", "").replace("&sslmode=require", "")

# asyncpg requires ssl="require" passed as a connect_arg (not a URL param).
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={"ssl": "require"},
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    """FastAPI dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        yield session
