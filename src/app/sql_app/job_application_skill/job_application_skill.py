from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.app.sql_app.database import Base


class JobApplicationSkill(Base):
    """
    Represents a skill associated with a Job application.

    Attributes:
        job_application_id (UUID): Foerign key referencing the related Job application.
        skill_id (UUID): Foerign key referencing the related Skill.

    Relationships:
        job_application (JobApplication): The associated Job application
        skill (Skill): The skill that is referenced.
    """

    __tablename__ = "job_application_skills"

    job_application_id = Column(
        UUID(as_uuid=True), ForeignKey("job_applications.id"), nullable=False
    )
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"))

    job_application = relationship("JobApplication", back_populates="skills")
    skill = relationship("Skill", back_populates="job_applications")
