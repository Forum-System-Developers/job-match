"""REST API endpoints"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    auth_router,
    category_router,
    company_router,
    google_auth_router,
    job_ad_router,
    job_application_router,
    job_requirement_router,
    professional_router,
)

api_router = APIRouter()

api_router.include_router(
    job_ad_router.router,
    prefix="/job-ads",
    tags=["Job Ads"],
)

api_router.include_router(
    job_requirement_router.router, prefix="/job-requirements", tags=["Job Requirements"]
)

api_router.include_router(
    company_router.router, prefix="/companies", tags=["Companies"]
)


api_router.include_router(
    professional_router.router, prefix="/professionals", tags=["Professionals"]
)

api_router.include_router(
    job_application_router.router, prefix="/job-applications", tags=["Job Applications"]
)

api_router.include_router(auth_router.router, prefix="/auth", tags=["Authentication"])

api_router.include_router(
    google_auth_router.router, prefix="/google-auth", tags=["Google Authentication"]
)

api_router.include_router(
    category_router.router, prefix="/categories", tags=["Categories"]
)
