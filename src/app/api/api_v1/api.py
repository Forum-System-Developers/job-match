"""REST API endpoints"""

from fastapi import APIRouter

from src.app.api.api_v1.endpoints.job_ad_router import router as job_ad_router

api_router = APIRouter()

api_router.include_router(
    job_ad_router,
    prefix="/job-ads",
    tags=["Job Ads"],
)
