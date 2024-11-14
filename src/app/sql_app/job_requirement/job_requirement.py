from enum import Enum

from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.sql_app.job_requirement.skill_level import SkillLevel
from src.app.sql_app.database import Base


class JobRequirement(Base):
    """
    Represents a job requirement in the database.

    Attributes:
        id (UUID): Unique identifier for the job requirement.
        description (str): Description of the job requirement.
        skill_level (SkillLevel): The skill level required for the job.
        created_at (datetime): Timestamp when the job requirement was created.
        updated_at (datetime): Timestamp when the job requirement was last updated.

    Relationships:
        job_ad_requirements (relationship): Relationship to the JobAdsRequirement model.
    """

    __tablename__ = "job_requirement"

    id = Column(
        UUID(as_uuid=True),
        server_default=func.uuid_generate_v4(),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    description = Column(String, nullable=False)
    skill_level = Column(Enum(SkillLevel), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    job_ad_requirements = relationship(
        "JobAdsRequirement", back_populates="job_requirement"
    )
