from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import pytz

from database import get_db

app = FastAPI(
    title="Python App API",
    description="A FastAPI application connected to Neon PostgreSQL.",
    version="1.0.0",
)


@app.get("/", tags=["Root"])
async def root():
    """Welcome route."""
    return {"message": "Welcome to the Python App! 🚀"}


# ──────────────────────────────────────────────
# Health check
# ──────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint.
    Verifies the API is running and the database connection is alive.
    """
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        db_status = f"unreachable: {exc}"

    return {
        "status": "healthy",
        "service": "python_app",
        "database": db_status,
    }


# ──────────────────────────────────────────────
# Current date / time
# ──────────────────────────────────────────────
@app.get("/datetime", tags=["Datetime"])
async def get_current_datetime(db: AsyncSession = Depends(get_db)):
    """
    Returns the current date and time from both the server and the database.
    """
    now_utc = datetime.now(pytz.utc)
    now_local = datetime.now()

    # Fetch current timestamp directly from Neon DB
    result = await db.execute(text("SELECT NOW() AS db_now"))
    db_now = result.scalar_one()

    return {
        "server": {
            "utc": {
                "date": now_utc.strftime("%Y-%m-%d"),
                "time": now_utc.strftime("%H:%M:%S"),
                "datetime": now_utc.isoformat(),
                "timezone": "UTC",
            },
            "local": {
                "date": now_local.strftime("%Y-%m-%d"),
                "time": now_local.strftime("%H:%M:%S"),
                "datetime": now_local.isoformat(),
                "timezone": "server local",
            },
        },
        "database": {
            "datetime": db_now.isoformat() if db_now else None,
            "timezone": "UTC (Neon DB)",
        },
    }
