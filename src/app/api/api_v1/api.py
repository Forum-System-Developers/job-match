"""REST API endpoints"""

from fastapi import APIRouter

from src.app.api.api_v1.endpoints.job_ad_router import router as job_ad_router
from src.app.api.api_v1.endpoints import profeesional_router


api_router = APIRouter()

api_router.include_router(
    job_ad_router,
    prefix="/job-ads",
    tags=["Job Ads"],
)

api_router.include_router(
    profeesional_router.router, prefix="/professionals", tags=["Professionals"]
)
