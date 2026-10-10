from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health_check():
    mode = "supabase" if settings.supabase_url and settings.supabase_service_role_key else "offline"
    return {
        "status": "ok",
        "mode": mode,
        "message": "LAYOVER API is running",
    }
