from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.sql_app.database import Base

if TYPE_CHECKING:
    from app.sql_app.job_application.job_application import JobApplication
    from app.sql_app.skill.skill import Skill


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

    __tablename__ = "job_application_skill"

    job_application_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_application.id"),
        nullable=False,
        primary_key=True,
    )
    skill_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skill.id"), primary_key=True
    )

    job_application: Mapped["JobApplication"] = relationship(
        "JobApplication", back_populates="skills", uselist=True, collection_class=list
    )
    skill: Mapped["Skill"] = relationship(
        "Skill", back_populates="job_applications", uselist=True, collection_class=list
    )
