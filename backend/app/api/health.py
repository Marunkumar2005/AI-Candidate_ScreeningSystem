from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "roles": settings.ROLES
    }
