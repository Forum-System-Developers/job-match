from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.sql_app.job_application.job_application_status import JobStatus
from src.app.sql_app.database import Base


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

    id = Column(
        UUID(as_uuid=True),
        server_default=func.uuid_generate_v4(),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    min_salary = Column(Numeric(10, 2), nullable=True)
    max_salary = Column(Numeric(10, 2), nullable=True)
    status = Column(Enum(JobStatus), nullable=False)
    description = Column(String, nullable=False)
    professional_id = Column(
        UUID(as_uuid=True), ForeignKey("profesional.id"), nullable=False
    )
    is_main = Column(Boolean, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=True,
    )
    job_ad = Column(UUID(as_uuid=True), ForeignKey("job_ad.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("category.id"), nullable=False)

    professional = relationship("Professional", back_populates="job_applications")
    category = relationship("Category", back_populates="job_applications")
    skills = relationship("JobApplicationSkill", back_populates="skill")
    matches = relationship("Match", back_populates="job_application")
