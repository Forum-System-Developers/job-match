import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.sql_app.database import Base
from app.sql_app.job_ad.job_ad_status import JobAdStatus
from app.sql_app.job_requirement.skill_level import SkillLevel
from app.sql_app.skill.skill import Skill

if TYPE_CHECKING:
    from app.sql_app import (
        Category,
        City,
        Company,
        JobAdSkill,
        JobAdsRequirement,
        Match,
    )


class JobAd(Base):
    """
    Represents a job advertisement.

    Attributes:
        id (uuid.UUID): Unique identifier for the job advertisement.
        company_id (uuid.UUID): Foreign key referencing the company.
        category_id (uuid.UUID): Foreign key referencing the category.
        location_id (uuid.UUID): Foreign key referencing the city.
        title (str): Title of the job advertisement.
        description (str): Description of the job advertisement.
        min_salary (float): Minimum salary offered for the job.
        max_salary (float): Maximum salary offered for the job.
        skill_level (SkillLevel): Required skill level for the job.
        status (JobAdStatus): Status of the job advertisement.
        created_at (datetime): Timestamp when the job advertisement was created.
        updated_at (datetime): Timestamp when the job advertisement was last updated.
    
    Relationships:
        job_ad_skills (list[JobAdSkill]): List of skills associated with the job advertisement.
        skills (list[Skill]): List of skills required for the job.
        category (Category): Category to which the job advertisement belongs.
        location (City): City where the job is located.
        company (Company): Company offering the job.
        matches (list[Match]): List of matches associated with the job advertisement.
    """

    __tablename__ = "job_ad"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        server_default=func.uuid_generate_v4(),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("company.id"), nullable=False
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("category.id"), nullable=False
    )
    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("city.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    min_salary: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    max_salary: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    skill_level: Mapped[SkillLevel] = mapped_column(Enum(SkillLevel), nullable=False)
    status: Mapped[JobAdStatus] = mapped_column(Enum(JobAdStatus), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    job_ad_skills: Mapped[list["JobAdSkill"]] = relationship(
        "JobAdSkill", back_populates="job_ad", uselist=True, collection_class=list
    )
    skills: Mapped[list[Skill]] = relationship(
        "Skill",
        secondary="job_ad_skills",
        back_populates="job_ads",
        uselist=True,
        collection_class=list,
    )
    category: Mapped["Category"] = relationship("Category", back_populates="job_ads")
    location: Mapped["City"] = relationship("City", back_populates="job_ads")
    company: Mapped["Company"] = relationship("Company", back_populates="job_ads")
    matches: Mapped[list["Match"]] = relationship(
        "Match", back_populates="job_ad", uselist=True, collection_class=list
    )
