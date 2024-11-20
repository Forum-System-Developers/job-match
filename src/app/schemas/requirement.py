from uuid import UUID

from pydantic import BaseModel

from app.sql_app import JobRequirement
from app.sql_app.job_requirement.skill_level import SkillLevel


class Requirement(BaseModel):
    description: str
    skill_level: SkillLevel

    class Config:
        from_attributes = True


class RequirementCreate(Requirement):
    pass


class RequirementResponse(Requirement):
    id: UUID
    company_id: UUID

    @classmethod
    def create(cls, requirement: JobRequirement) -> "RequirementResponse":
        return cls(
            id=requirement.id,
            description=requirement.description,
            skill_level=requirement.skill_level,
            company_id=requirement.company_id,
        )
