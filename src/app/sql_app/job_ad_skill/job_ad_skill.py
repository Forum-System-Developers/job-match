import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.sql_app.database import Base

if TYPE_CHECKING:
    from app.sql_app import JobAd, Skill


class JobAdSkill(Base):
    """
    Represents the association between job advertisements and skills.

    Attributes:
        __tablename__ (str): The name of the table in the database.
        job_ad_id (uuid.UUID): The ID of the job advertisement. This is a foreign key referencing the "job_ad" table.
        skill_id (uuid.UUID): The ID of the skill. This is a foreign key referencing the "skill" table.
        job_ad (JobAd): The job advertisement associated with this skill.
        skill (Skill): The skill associated with this job advertisement.
    """

    __tablename__ = "job_ad_skill"

    job_ad_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_ad.id"),
        nullable=False,
        primary_key=True,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skill.id"), primary_key=True
    )

    job_ad: Mapped["JobAd"] = relationship("JobAd", back_populates="job_ad_skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="job_ad_skills")
