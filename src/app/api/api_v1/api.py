"""REST API endpoints"""

from fastapi import APIRouter

from src.app.api.api_v1.endpoints import job_ad

api_router = APIRouter()

api_router.include_router(
    job_ad.router,
    prefix="/job-ad",
    tags=["Job Ad"],
)
