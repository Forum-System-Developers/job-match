"""REST API endpoints"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import job_ad_router, professional_router

api_router = APIRouter()

api_router.include_router(
    job_ad_router.router,
    prefix="/job-ads",
    tags=["Job Ads"],
)

api_router.include_router(
    professional_router.router, prefix="/professionals", tags=["Professionals"]
)
