import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.sql_app.database import Base
from app.sql_app.job_ad.job_ad_status import JobAdStatus

if TYPE_CHECKING:
    from app.sql_app.category.category import Category
    from app.sql_app.city.city import City
    from app.sql_app.company.company import Company
    from app.sql_app.job_ad_requirement.job_ads_requirement import JobAdsRequirement
    from app.sql_app.match.match import Match


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
    status: Mapped[JobAdStatus] = mapped_column(Enum(JobAdStatus), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    job_ads_requirements: Mapped["JobAdsRequirement"] = relationship(
        "JobAdsRequirement",
        back_populates="job_ad",
        uselist=True,
        collection_class=list,
    )
    category: Mapped["Category"] = relationship("Category", back_populates="job_ads")
    location: Mapped["City"] = relationship("City", back_populates="job_ads")
    company: Mapped["Company"] = relationship("Company", back_populates="job_ads")
    matches: Mapped[list["Match"]] = relationship(
        "Match", back_populates="job_ad", uselist=True, collection_class=list
    )
