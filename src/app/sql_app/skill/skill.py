import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.sql_app.database import Base

if TYPE_CHECKING:
    from app.sql_app import JobAdSkill, JobApplicationSkill


class Skill(Base):
    """
    Represents a skill entity in the database.
    Attributes:
        id (uuid.UUID): Unique identifier for the skill.
        category_id (uuid.UUID): Foreign key referencing the category to which the skill belongs.
        name (str): Name of the skill.
        job_ad_skills (list[JobAdSkill]): List of job advertisement skills associated with this skill.
        job_application_skills (list[JobApplicationSkill]): List of job application skills associated with this skill.
    """

    __tablename__ = "skill"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        server_default=func.uuid_generate_v4(),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("category.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    job_ad_skills: Mapped[list["JobAdSkill"]] = relationship(
        "JobAdSkill",
        back_populates="skill",
        uselist=True,
        collection_class=list,
    )
    job_application_skills: Mapped[list["JobApplicationSkill"]] = relationship(
        "JobApplicationSkill",
        back_populates="skill",
        uselist=True,
        collection_class=list,
    )
