from uuid import UUID

from pydantic import BaseModel

from app.sql_app.skill.skill import Skill


class SkillBase(BaseModel):
    """
    SkillBase is a Pydantic model that represents the base schema for a skill.

    Attributes:
        name (str): The name of the skill.

    Config:
        from_attributes (bool): Configuration to allow population of model attributes from dictionaries.
    """

    name: str

    class Config:
        from_attributes = True


class SkillCreate(SkillBase):
    """
    SkillCreate schema for creating a new skill.

    Attributes:
        name (str): The name of the skill.
        category_id (UUID): The unique identifier of the category to which the skill belongs.
    """

    category_id: UUID


class SkillResponse(SkillBase):
    """
    SkillResponse is a Pydantic model that represents the response schema for a skill.

    Attributes:
        id (UUID): The unique identifier of the skill.
        category_id (UUID): The unique identifier of the category to which the skill belongs.
    """

    id: UUID
    category_id: UUID

    @classmethod
    def create(cls, skill: Skill) -> "SkillResponse":
        return cls(
            id=skill.id,
            name=skill.name,
            category_id=skill.category_id,
        )
