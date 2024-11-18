from uuid import UUID

from pydantic import BaseModel

from app.sql_app.job_requirement.skill_level import SkillLevel


class SkillBase(BaseModel):
    """
    Pydantic model representing a skill associated with a specific skill level.

    Attributes:
        name (str): Skill name.
        level (SkillLevel): Enum representing the level of proficiency for the skill.

    """

    name: str
    level: SkillLevel

    class Config:
        use_enum_values = True


class Requirement(SkillBase):
    pass


class RequirementCreate(SkillBase):
    pass


class RequirementResponse(SkillBase):
    id: UUID
    company_id: UUID
