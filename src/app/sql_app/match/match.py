from sqlalchemy import Column, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.app.sql_app.database import Base


class Match(Base):
    """
    Represents a match between a job advertisement and a job application.

    Attributes:
        job_ad_id (UUID): The unique identifier of the job advertisement.
        job_application_id (UUID): The unique identifier of the job application.
        created_at (DateTime): The timestamp when the match was created.

    Relationships:
        job_ad (JobAd): The job advertisement associated with this match.
        job_application (JobApplication): The job application associated with this match.
    """

    __tablename__ = "match"

    job_ad_id = Column(UUID(as_uuid=True), ForeignKey("job_ad.id"), primary_key=True)
    job_application_id = Column(
        UUID(as_uuid=True), ForeignKey("job_application.id"), primary_key=True
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    job_ad = relationship("JobAd", back_populates="matches")
    job_application = relationship("JobApplication", back_populates="matches")
