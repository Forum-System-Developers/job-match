from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, condecimal

from app.schemas.custom_types import Salary
from app.schemas.requirement import Requirement
from app.sql_app.job_ad.job_ad import JobAd
from app.sql_app.job_ad.job_ad_status import JobAdStatus


class BaseJobAd(BaseModel):
    title: str
    description: str
    location_id: UUID
    category_id: UUID
    min_salary: condecimal(gt=0, max_digits=10, decimal_places=2)  # type: ignore
    max_salary: condecimal(gt=0, max_digits=10, decimal_places=2)  # type: ignore

    class Config:
        from_attributes = True


class JobAdResponse(BaseJobAd):
    id: UUID
    status: JobAdStatus
    requirements: list[Requirement] = []
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, job_ad: JobAd) -> "JobAdResponse":
        requirements = [
            Requirement.model_validate(job_ad_req.job_requirement)
            for job_ad_req in job_ad.job_ads_requirements
        ]
        return cls(
            id=job_ad.id,
            title=job_ad.title,
            description=job_ad.description,
            location_id=job_ad.location_id,
            category_id=job_ad.category_id,
            min_salary=job_ad.min_salary,
            max_salary=job_ad.max_salary,
            status=job_ad.status,
            requirements=requirements,
            created_at=job_ad.created_at,
            updated_at=job_ad.updated_at,
        )


class JobAdCreate(BaseJobAd):
    pass


class JobAdUpdate(BaseModel):
    title: str | None
    description: str | None
    location: str | None
    min_salary: Salary | None  # type: ignore
    max_salary: Salary | None  # type: ignore
    status: JobAdStatus | None
