from sqlalchemy import Column, DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.app.sql_app.database import Base
from src.app.sql_app.job_ad.job_ad_status import JobAdStatus


class JobAd(Base):
    """
    Represents a job advertisement in the database.

    Attributes:
        id (UUID): Unique identifier for the job advertisement.
        category_id (UUID): Foreign key referencing the category of the job ad.
        location_id (UUID): Foreign key referencing the location of the job ad.
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
        category (relationship): Relationship to the Category model.
        location (relationship): Relationship to the City model.
        matches (relationship): Relationship to the Match model.
    """

    __tablename__ = "job_ad"

    id = Column(
        UUID(as_uuid=True),
        server_default=func.uuid_generate_v4(),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    company_id = Column(UUID(as_uuid=True), ForeignKey("company.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("category.id"), nullable=False)
    location_id = Column(UUID(as_uuid=True), ForeignKey("city.id"), nullable=False)
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
    category = relationship("Category", back_populates="job_ads")
    location = relationship("City", back_populates="job_ads")
    company = relationship("Company", back_populates="job_ads")
    matches = relationship("Match", back_populates="job_ad")
