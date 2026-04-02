from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Health check")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Returns the health status of the API and its dependencies.
    Used by monitoring tools and container orchestrator
    """
    Settings = get_settings()
    db_status = "healthy"

    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    is_healthy = db_status == "healthy"

    return {
        "success": True,
        "data": {
            "status": "healthy" if is_healthy else "degraded",
            "app_name": Settings.APP_NAME,
            "checks": {"database": db_status},
        },
    }
