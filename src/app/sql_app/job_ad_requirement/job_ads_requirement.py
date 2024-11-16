from sqlalchemy import Column, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.sql_app.database import Base


class JobAdsRequirement(Base):
    """
    JobAdsRequirement is a SQLAlchemy model representing the requirements for job advertisements.

    Attributes:
        job_ad_id (UUID): Foreign key referencing the ID of the job advertisement.
        job_application_id (UUID): Foreign key referencing the ID of the job application.
        created_at (DateTime): Timestamp when the record was created, with timezone support.
        updated_at (DateTime): Timestamp when the record was last updated, with timezone support.

    Relationships:
        job_ad (relationship): Relationship to the JobAd model.
        job_application (relationship): Relationship to the JobApplication model.
    """

    __tablename__ = "job_ads_requirement"

    job_ad_id = Column(
        UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, primary_key=True
    )
    job_application_id = Column(
        UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, primary_key=True
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    job_ad = relationship("JobAd", back_populates="job_ads_requirements")
    job_application = relationship(
        "JobApplication", back_populates="job_ads_requirements"
    )
