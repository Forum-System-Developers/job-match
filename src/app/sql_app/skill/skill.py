from sqlalchemy import Column, func, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.app.sql_app.database import Base


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

    __tablename__ = "job_applications"

    id = Column(
        UUID(as_uuid=True),
        server_default=func.uuid_generate_v4(),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    skill = Column(String, unique=True, nullable=False)
    # level = Column(Enum("SkillLevel"), nullable=False)

    job_applications = relationship(
        "JobApplicationSkills", back_populates="job_application"
    )
