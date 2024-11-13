from sqlalchemy import Column, DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.app.sql_app.database import Base
from app.sql_app.job_ad.job_ad_status import JobAdStatus


class JobAd(Base):
    """
    Represents a job advertisement in the database.

    Attributes:
        id (UUID): Unique identifier for the job advertisement.
        company_id (UUID): Foreign key referencing the company that posted the job ad.
        title (str): Title of the job position.
        description (str): Description of the job position.
        min_salary (Decimal): Minimum salary offered for the job position.
        max_salary (Decimal): Maximum salary offered for the job position.
        status (JobAdStatus): Current status of the job advertisement.
        created_at (datetime): Timestamp when the job advertisement was created.
        updated_at (datetime): Timestamp when the job advertisement was last updated.

    Relationships:
        job_ads_requirements (relationship): Relationship to the JobAdsRequirement model.
        company (relationship): Relationship to the Company model.
    """

    __tablename__ = "job_ads"

    id = Column(
        UUID(as_uuid=True),
        server_default=func.uuid_generate_v4(),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    min_salary = Column(Numeric(10, 2), nullable=False)
    max_salary = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(JobAdStatus), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    job_ads_requirements = relationship("JobAdsRequirement", back_populates="job_ad")
    company = relationship("Company", back_populates="job_ads")
