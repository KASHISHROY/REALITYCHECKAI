from fastapi import APIRouter

from app.config import get_settings
from app.schemas.health import HealthCheck

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthCheck)
async def health_check() -> HealthCheck:
    settings = get_settings()
    return HealthCheck(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
    )

