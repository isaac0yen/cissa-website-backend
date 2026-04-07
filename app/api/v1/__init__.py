from fastapi import APIRouter

from app.api.v1.auth.routes import auth
from app.api.v1.announcement.routes import signatory, announcement
from app.api.v1.event.routes import event

main_router = APIRouter(prefix="/api/v1")

main_router.include_router(router=auth)
main_router.include_router(router=signatory)
main_router.include_router(router=announcement)
main_router.include_router(router=event)
