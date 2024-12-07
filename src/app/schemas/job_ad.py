from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, condecimal

from app.schemas.city import City
from app.schemas.custom_types import Salary
from app.schemas.skill import SkillBase
from app.services.enums.job_ad_status import JobAdStatus
from app.services.enums.skill_level import SkillLevel
from app.sql_app.job_ad.job_ad import JobAd


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

    @classmethod
    def _from_job_ad(cls, job_ad: JobAd, **kwargs):
        return cls(
            title=job_ad.title,
            description=job_ad.description,
            category_id=job_ad.category_id,
            category_name=job_ad.category.title,
            skill_level=job_ad.skill_level,
            city=City(id=job_ad.location.id, name=job_ad.location.name),
            min_salary=job_ad.min_salary,
            max_salary=job_ad.max_salary,
            **kwargs,
        )

    @classmethod
    def create(cls, job_ad: JobAd) -> "JobAdPreview":
        return cls._from_job_ad(job_ad)


class JobAdResponse(JobAdPreview):
    id: UUID
    company_id: UUID
    status: JobAdStatus
    required_skills: list[SkillBase] = []
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, job_ad: JobAd) -> "JobAdResponse":
        required_skills = [SkillBase.model_validate(skill) for skill in job_ad.skills]
        return cls._from_job_ad(
            job_ad,
            id=job_ad.id,
            company_id=job_ad.company_id,
            status=job_ad.status,
            required_skills=required_skills,
            created_at=job_ad.created_at,
            updated_at=job_ad.updated_at,
        )


class JobAdCreate(BaseJobAd):
    location_id: UUID


class JobAdUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    skill_level: SkillLevel | None = None
    location: str | None = None
    min_salary: Salary | None = None  # type: ignore
    max_salary: Salary | None = None  # type: ignore
    status: JobAdStatus | None = None
