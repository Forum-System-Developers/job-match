import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.sql_app.database import Base

if TYPE_CHECKING:
    from app.sql_app.job_ad.job_ad import JobAd
    from app.sql_app.job_requirement.job_requirement import JobRequirement


class JobAdsRequirement(Base):
    """
    Represents the requirements for a job advertisement.

    Attributes:
        job_ad_id (uuid.UUID): The unique identifier of the job advertisement.
        job_application_id (uuid.UUID): The unique identifier of the job application.
        created_at (datetime): The timestamp when the requirement was created.
        updated_at (datetime): The timestamp when the requirement was last updated.

    Relationships:
        job_ad (JobAd): The relationship to the JobAd model.
        job_requirement (JobRequirement): The relationship to the JobRequirement model.
    """

    __tablename__ = "job_ads_requirement"

    job_ad_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, primary_key=True
    )
    job_application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    job_ad: Mapped["JobAd"] = relationship(
        "JobAd", back_populates="job_ads_requirements"
    )
    job_requirement: Mapped["JobRequirement"] = relationship(
        "JobRequirement", back_populates="job_ads_requirements"
    )
