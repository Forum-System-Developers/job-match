import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.sql_app.database import Base
from app.sql_app.job_requirement.skill_level import SkillLevel

if TYPE_CHECKING:
    from app.sql_app.job_application_skill.job_application_skill import (
        JobApplicationSkill,
    )


class Skill(Base):
    """
    Represents a skill
    Attributes:
        id (UUID): The unique identifier of the Skill.
        skill (str): Represents the skill title.
        level (SkillLevel): Represents the level of proficiency the Professional has indicated for this skill.

    Relationships:
        job_applications (list[JobApplicationSkills]): A list of Job applications that are associated with this skill.
    """

    __tablename__ = "skill"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        server_default=func.uuid_generate_v4(),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    skill: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    level: Mapped[SkillLevel] = mapped_column(Enum(SkillLevel), nullable=False)

    job_applications: Mapped["JobApplicationSkill"] = relationship(
        "JobApplicationSkills",
        back_populates="job_application",
        uselist=True,
        collection_class=list,
    )
