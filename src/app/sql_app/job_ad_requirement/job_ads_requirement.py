import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.sql_app.database import Base

if TYPE_CHECKING:
    from app.sql_app import JobAd, JobRequirement


class JobAdsRequirement(Base):
    """
    JobAdsRequirement is a SQLAlchemy model representing the relationship between job advertisements and job requirements.

    Attributes:
        job_ad_id (uuid.UUID): The unique identifier of the job advertisement. It is a foreign key referencing the 'user.id' column.
        job_requirement_id (uuid.UUID): The unique identifier of the job requirement. It is a foreign key referencing the 'job_requirement.id' column.
        created_at (datetime): The timestamp when the record was created. It defaults to the current time.
        updated_at (datetime): The timestamp when the record was last updated. It defaults to the current time.

    Relationships:
        job_ad (JobAd): The relationship to the JobAd model, back_populated by 'job_ads_requirements'.
        job_requirement (JobRequirement): The relationship to the JobRequirement model, back_populated by 'job_ads_requirements'.
    """

    __tablename__ = "job_ads_requirement"

    job_ad_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_ad.id"), nullable=False, primary_key=True
    )
    job_requirement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_requirement.id"),
        nullable=False,
        primary_key=True,
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
