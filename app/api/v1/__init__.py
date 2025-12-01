from fastapi import APIRouter

from app.api.v1.auth.routes import auth
from app.api.v1.announcement.routes import signatory, announcement
from app.api.v1.student_profile.routes import student_profile
from app.api.v1.tests.routes import test_router
from app.api.v1.questions.routes import question_router

main_router = APIRouter(prefix="/api/v1")

main_router.include_router(router=auth)
main_router.include_router(router=student_profile)
main_router.include_router(router=test_router)
main_router.include_router(router=signatory)
main_router.include_router(router=announcement)
main_router.include_router(router=question_router)
