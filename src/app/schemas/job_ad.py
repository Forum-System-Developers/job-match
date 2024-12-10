from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, condecimal

from app.schemas.city import City
from app.schemas.custom_types import Salary
from app.schemas.skill import SkillBase
from app.services.enums.job_ad_status import JobAdStatus
from app.services.enums.skill_level import SkillLevel


class BaseJobAd(BaseModel):
    title: str
    description: str
    skill_level: SkillLevel
    category_id: UUID
    min_salary: condecimal(gt=0, max_digits=10, decimal_places=2)  # type: ignore
    max_salary: condecimal(gt=0, max_digits=10, decimal_places=2)  # type: ignore

    class Config:
        from_attributes = True


class JobAdPreview(BaseJobAd):
    city: City
    category_name: str


class JobAdResponse(JobAdPreview):
    id: UUID
    company_id: UUID
    status: JobAdStatus
    required_skills: list[SkillBase] = []
    created_at: datetime
    updated_at: datetime


class JobAdCreate(BaseJobAd):
    location_id: UUID


class JobAdCreateFull(JobAdCreate):
    company_id: UUID


class JobAdUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    skill_level: SkillLevel | None = None
    location: str | None = None
    min_salary: Salary | None = None  # type: ignore
    max_salary: Salary | None = None  # type: ignore
    status: JobAdStatus | None = None
