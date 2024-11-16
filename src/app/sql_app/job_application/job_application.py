from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.sql_app.database import Base
from app.sql_app.job_application.job_application_status import JobStatus

if TYPE_CHECKING:
    from app.sql_app.category.category import Category
    from app.sql_app.job_application_skill.job_application_skill import (
        JobApplicationSkill,
    )
    from app.sql_app.match.match import Match
    from app.sql_app.professional.professional import Professional


class JobApplication(Base):
    """
    Represents a job application entity in the app.

    Attributes:
        id (UUID): The unique identifier of the Job application.
        min_salary (float): Lower limit of the salary range the Professional is applying for.
        max_salary (float): Upper limit of the salary the Professional is applying for.
        status (JobStatus): The status of the Job application.
        description (str): The Job application description.
        professional_id (UUID): Foreign key referencing the Professional associated with this Job application.
        is_main (bool): Property representing if this is the Professional's main application. This property is nullable.
        created_at (datetime): Timestamp when the job application was created.
        updated_at (datetime): Timestamp when the job application was last updated.
        category_id (UUID): The identifier of the Company this Job application has been matched with.

    Relationships:
        professional (Professional): The user who created the job application.
        category (Category): The category for the Job Ad that was matched with the Job Application.
        skills (list[Skill]): The skillset indicated on this job application.
    """

    __tablename__ = "job_application"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        server_default=func.uuid_generate_v4(),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    min_salary: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    max_salary: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    status: Mapped[str] = mapped_column(Enum(JobStatus), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    professional_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("professional.id"), nullable=False
    )
    is_main: Mapped[bool] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=True,
    )
    job_ad: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_ad.id"), nullable=False
    )
    category_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("category.id"), nullable=False
    )

    professional: Mapped["Professional"] = relationship(
        "Professional", back_populates="job_applications"
    )
    category: Mapped["Category"] = relationship(
        "Category", back_populates="job_applications"
    )
    skills: Mapped["JobApplicationSkill"] = relationship(
        "JobApplicationSkill",
        back_populates="skill",
        uselist=True,
        collection_class=list,
    )
    matches: Mapped["Match"] = relationship(
        "Match", back_populates="job_application", uselist=True, collection_class=list
    )
