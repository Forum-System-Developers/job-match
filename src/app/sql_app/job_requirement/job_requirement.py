import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.sql_app.database import Base
from app.sql_app.job_requirement.skill_level import SkillLevel

if TYPE_CHECKING:
    from app.sql_app import JobAdsRequirement


class JobRequirement(Base):
    """
    Represents a job requirement in the job matching application.

    Attributes:
        id (uuid.UUID): Unique identifier for the job requirement.
        company_id (uuid.UUID): Identifier for the associated company. Can be null.
        description (str): Description of the job requirement.
        skill_level (SkillLevel): Required skill level for the job.
        created_at (datetime): Timestamp when the job requirement was created.
        updated_at (datetime): Timestamp when the job requirement was last updated.

    Relationships:
        job_ad_requirements (list[JobAdsRequirement]): List of job ad requirements associated with this job requirement.
    """

    __tablename__ = "job_requirement"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        server_default=func.uuid_generate_v4(),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("company.id"), nullable=True
    )
    description: Mapped[str] = mapped_column(String, nullable=False)
    skill_level: Mapped[SkillLevel] = mapped_column(Enum(SkillLevel), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    job_ads_requirements: Mapped[list["JobAdsRequirement"]] = relationship(
        "JobAdsRequirement",
        back_populates="job_requirement",
        uselist=True,
        collection_class=list,
    )
