from fastapi import APIRouter
from . import auth, leads, conversations, campaigns, templates, analytics, credits

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(leads.router, prefix="/leads", tags=["Leads"])
router.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
router.include_router(campaigns.router, prefix="/campaigns", tags=["Campaigns"])
router.include_router(templates.router, prefix="/templates", tags=["Templates"])
router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
router.include_router(credits.router, prefix="/credits", tags=["Credits"])
