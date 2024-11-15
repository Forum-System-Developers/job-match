import datetime
from uuid import UUID

from pydantic import BaseModel, condecimal

from src.app.sql_app.job_ad.job_ad_status import JobAdStatus


class BaseJobAd(BaseModel):
    title: str
    description: str
    location: str
    min_salary: condecimal(gt=0, max_digits=10, decimal_places=2)  # type: ignore
    max_salary: condecimal(gt=0, max_digits=10, decimal_places=2)  # type: ignore

    class Config:
        from_attributes = True


class JobAdResponse(BaseJobAd):
    id: UUID
    status: JobAdStatus
    created_at: datetime
    updated_at: datetime


class JobAdCreate(BaseJobAd):
    company_id: UUID
