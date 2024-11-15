"""REST API endpoints"""

from fastapi import APIRouter

from src.app.api.api_v1.endpoints import job_ad
from src.app.api.api_v1.endpoints import profeesional_router

api_router = APIRouter()

api_router.include_router(
    job_ad.router,
    prefix="/job-ad",
    tags=["Job Ad"],
)

api_router.include_router(
    profeesional_router.router, prefix="/professionals", tags=["Professionals"]
)
